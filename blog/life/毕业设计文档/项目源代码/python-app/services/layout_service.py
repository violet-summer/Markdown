import json
import logging
import os
from pathlib import Path

from celery import Celery
import pika

from app.schemas.layout import LayoutParams
from app.services.procgen_python.generate_process import Generator
from app.services.procgen_python.main import  generate_from_artifacts
from app.services.proto import city_mq_contract_pb2
from app.services.storage.file import FileUtil

celery_app = Celery('layout_tasks', broker='redis://localhost:6379/0')

EXCHANGE_NAME = "city-exchange"


LAYOUT_RESULT_QUEUE = "layout_result"
LAYOUT_PROGRESS_QUEUE = "layout_progress"
MODEL_RESULT_QUEUE = "model_result"
MODEL_PROGRESS_QUEUE = "model_progress"
LAYOUT_TASK_QUEUE = "layout_task"
MODEL_TASK_QUEUE = "model_task"


# RabbitMQ消息推送

def send_progress(channel, queue, task_id, progress, status, message=None):
    progress_msg = city_mq_contract_pb2.LayoutProgressMessage()
    progress_msg.taskId = task_id
    progress_msg.progress = progress
    progress_msg.status = status
    progress_msg.message = message or ""
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=queue,
        body=progress_msg.SerializeToString()
    )
    logging.info(f"[RabbitMQ] Progress sent to {queue}: task_id={task_id}, progress={progress}, status={status}, message={message}")


# Celery任务
# 当前保存目录将会有java业务端管理并告知，暂且定义为用户目录然后下方的特定的布局目录，python端此时不需要关心
# 目录的位置
@celery_app.task
def celery_generate_layout(taskid, params, output_dir, progress_queue, result_queue, rabbitmq_url):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=progress_queue, durable=True)
    channel.queue_bind(queue=progress_queue, exchange=EXCHANGE_NAME, routing_key=progress_queue)
    channel.queue_declare(queue=result_queue, durable=True)
    channel.queue_bind(queue=result_queue, exchange=EXCHANGE_NAME, routing_key=result_queue)
    send_progress(channel, progress_queue, taskid, 10, "started", "布局生成任务已启动")
    file_util = FileUtil()
    try:
        params_path = str(Path(output_dir) / "params.json")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        with open(params_path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2, ensure_ascii=False)
        params_instance = LayoutParams(**params)
        max_retries = 1
        for attempt in range(max_retries):
            try:
                os.makedirs(output_dir, exist_ok=True)
                main_instance = Generator(params_var=params_instance, dir=output_dir)
                stages = [
                    (main_instance.generate_layout_stage_0, 10, "stage_0", "基础布局生成"),
                    (main_instance.generate_layout_stage_1_water_line, 20, "stage_1", "水线生成"),
                    (main_instance.generate_layout_stage_2_water_polygon, 30, "stage_2", "水域多边形生成"),
                    (main_instance.generate_layout_stage_3_main_and_major_roads, 40, "stage_3", "主干道生成"),
                    (main_instance.generate_layout_stage_4_big_parks, 50, "stage_4", "大型公园生成"),
                    (main_instance.generate_layout_stage_5_minor_roads, 60, "stage_5", "次级道路生成"),
                    (main_instance.generate_layout_stage_6_small_parks, 70, "stage_6", "小型公园生成"),
                    (main_instance.generate_layout_stage_7_polygon, 80, "stage_7", "多边形布局生成"),
                    (main_instance.generate_layout_stage_8_export_svg_json, 90, "stage_8", "导出SVG与JSON"),
                ]
                # 遍历分阶段调用
                for func, progress, stage, msg in stages:
                    try:
                        func()
                        send_progress(channel, progress_queue, taskid, progress, stage, f"{msg}完成")
                    except Exception as e:
                        # GenerationStageError 处理
                        if hasattr(e, 'stage') and hasattr(e, 'message'):
                            error_stage = getattr(e, 'stage', stage)
                            error_msg = getattr(e, 'message', str(e))
                            send_progress(channel, progress_queue, taskid, 0, "failed", f"{error_stage}失败: {error_msg}")
                        else:
                            send_progress(channel, progress_queue, taskid, 0, "failed", f"{msg}失败: {e}")
                        raise
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.error(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
                else:
                    logging.error(f"Failed after {max_retries} attempts. Error: {e}")
                    raise
        # 最终布局生成结束，上传 layout.svg 和 params.json 到 MinIO
        svg_path = Path(output_dir) / "layout.svg"
        params_json_path = Path(output_dir) / "params.json"
        # 以 assets/ 开头的相对路径，假设 output_dir 形如 assets/6/xxx/layout_test-layout-consumer
        # 若 output_dir 不是以 assets/ 开头，则补齐
        def ensure_assets_prefix(p):
            p = str(p).replace("\\", "/")
            if not p.startswith("assets/"):
                # 只取 assets/ 之后的部分
                idx = p.find("assets/")
                if idx >= 0:
                    p = p[idx:]
                else:
                    p = f"assets/{p.lstrip('/')}"
            return p
        svg_minio_path = ensure_assets_prefix(svg_path)
        params_minio_path = ensure_assets_prefix(params_json_path)
        if svg_path.exists():
            file_util.upload_file(svg_path, svg_minio_path)
        if params_json_path.exists():
            file_util.upload_file(params_json_path, params_minio_path)
        send_progress(channel, progress_queue, taskid, 100, "completed", "布局生成完成")
        result_msg = city_mq_contract_pb2.LayoutTaskResultMessage()
        result_msg.taskId = taskid
        result_msg.status = "success"
        result_msg.svgUrl = svg_minio_path
        result_msg.message = "布局生成成功"
    except Exception as e:
        result_msg = city_mq_contract_pb2.LayoutTaskResultMessage()
        result_msg.taskId = taskid
        result_msg.status = "error"
        result_msg.svgUrl = ""
        result_msg.message = f"布局生成失败: {e}"
        send_progress(channel, progress_queue, taskid, 0, "failed", str(e))
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=result_queue,
        body=result_msg.SerializeToString()
    )
    logging.info(f"[RabbitMQ] Layout result sent to {result_queue}: task_id={taskid}, status={result_msg.status}, message={result_msg.message}")
    connection.close()


@celery_app.task
def celery_generate_model(task_id, output_dir, layout_json_path, progress_queue, result_queue, rabbitmq_url):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=progress_queue, durable=True)
    channel.queue_bind(queue=progress_queue, exchange=EXCHANGE_NAME, routing_key=progress_queue)
    channel.queue_declare(queue=result_queue, durable=True)
    channel.queue_bind(queue=result_queue, exchange=EXCHANGE_NAME, routing_key=result_queue)
    send_progress(channel, progress_queue, task_id, 10, "start_generate_models", "模型生成任务已启动")
    file_util = FileUtil()
    try:
        logging.info("模型生成开始")
        models_paths = generate_from_artifacts(json_layout_path=layout_json_path, output_dir_path=output_dir)
        logging.info("模型生成完成，正在准备结果")
        send_progress(channel, progress_queue, task_id, 80, "generating_models", "模型生成中")
        result_msg = city_mq_contract_pb2.ModelTaskResultMessage()
        result_msg.taskId = task_id
        result_msg.status = "success"
        result_msg.message = "模型生成成功"
        # 上传所有模型文件到 MinIO
        def ensure_assets_prefix(p):
            p = str(p).replace("\\", "/")
            if not p.startswith("assets/"):
                idx = p.find("assets/")
                if idx >= 0:
                    p = p[idx:]
                else:
                    p = f"assets/{p.lstrip('/')}"
            return p
        for k, v in models_paths.items():
            # if v and Path(v).exists():
            minio_path = ensure_assets_prefix(v)
            #     file_util.upload_file(v, minio_path)
            result_msg.modelsPaths[k] = minio_path
        send_progress(channel, progress_queue, task_id, 100, "completed", "模型生成完成")
    except Exception as e:
        logging.error(f"模型生成出错: {e}")
        result_msg = city_mq_contract_pb2.ModelTaskResultMessage()
        result_msg.taskId = task_id
        result_msg.status = "error"
        result_msg.message = str(e)
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=result_queue,
        body=result_msg.SerializeToString()
    )
    logging.info(f"[RabbitMQ] Model result sent to {result_queue}: task_id={task_id}, status={result_msg.status}, message={result_msg.message}")
    connection.close()


# 布局生成worker

def rabbitmq_layout_worker(rabbitmq_url, consume_queue, result_queue, progress_queue, result_dir):
    print(f"[RabbitMQLayoutWorker] 启动，监听队列: {consume_queue}，服务器: {rabbitmq_url}")
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=consume_queue, durable=True)
    channel.queue_bind(queue=consume_queue, exchange=EXCHANGE_NAME, routing_key=consume_queue)
    def callback(ch, method, properties, body):
        try:
            task_msg = city_mq_contract_pb2.LayoutTaskMessage()
            task_msg.ParseFromString(body)
            taskid = task_msg.taskId
            params = json.loads(task_msg.params)
            output_dir = task_msg.layoutDir
            print(f"[RabbitMQLayoutWorker] 调用 celery_generate_layout: taskid={taskid}, output_dir={output_dir}")
            celery_generate_layout.delay(taskid, params, output_dir, progress_queue, result_queue, rabbitmq_url)
        except Exception as e:
            print(f"[RabbitMQLayoutWorker] 消费消息异常: {e}")
    channel.basic_consume(queue=consume_queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


# 模型生成worker

def rabbitmq_model_worker(rabbitmq_url, consume_queue, result_queue, progress_queue, result_dir):
    print(f"[RabbitMQModelWorker] 启动，监听队列: {consume_queue}，服务器: {rabbitmq_url}")
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=consume_queue, durable=True)
    channel.queue_bind(queue=consume_queue, exchange=EXCHANGE_NAME, routing_key=consume_queue)
    def callback(ch, method, properties, body):
        try:
            task_msg = city_mq_contract_pb2.ModelTaskMessage()
            task_msg.ParseFromString(body)
            taskid = task_msg.taskId
            output_dir = task_msg.outputDir
            layout_json_path = task_msg.layoutJsonFilePath
            print(f"[RabbitMQModelWorker] 调用 celery_generate_model: taskid={taskid}, output_dir={output_dir}")
            celery_generate_model.delay(taskid, output_dir, layout_json_path, progress_queue, result_queue, rabbitmq_url)
        except Exception as e:
            print(f"[RabbitMQModelWorker] 消费消息异常: {e}")
    channel.basic_consume(queue=consume_queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
