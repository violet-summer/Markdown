import threading
from pathlib import Path

from app.core.config import settings
from app.services.layout_service import rabbitmq_model_worker, rabbitmq_layout_worker


def start_rabbitmq_workers():
    rabbitmq_url = getattr(settings, 'rabbitmq_url', 'amqp://guest:helloworld@localhost:5672/')
    assets_dir = str(Path(settings.assets_storage_dir))
    threading.Thread(
        target=rabbitmq_model_worker,
        args=(
            rabbitmq_url,
            "model_task",      # consume_queue
            "model_result",    # result_queue
            "model_progress",  # progress_queue
            assets_dir,         # result_dir
        ),
        daemon=True
    ).start()
    threading.Thread(
        target=rabbitmq_layout_worker,
        args=(
            rabbitmq_url,
            "layout_task",     # consume_queue
            "layout_result",   # result_queue
            "layout_progress", # progress_queue
            assets_dir,         # result_dir
        ),
        daemon=True
    ).start()

import subprocess
import sys
import os


def start_celery_worker():
    cmd = [
        sys.executable, "-m", "celery",
        "-A", "app.workers.celery_app",
        "worker",
        "--loglevel", "INFO",
        # "--pool=solo",  # Windows 必须指定 solo
        "--pool=threads",  # 使用线程池
        "--concurrency=4",  # 线程数为4
    ]
    subprocess.Popen(cmd, env=os.environ.copy())

if __name__ == "__main__":
    start_rabbitmq_workers()
    start_celery_worker()
    threading.Event().wait()
