import os
import threading
import time
import uuid
from datetime import timedelta

import cv2
import nacos
import requests
# from Cython.Includes.cpython.time import result
from flask import Flask, render_template, request, jsonify
from paddleocr import PaddleOCR
from werkzeug.utils import secure_filename
import socket
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(hours=1)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
SERVER_ADDRESS = "127.0.0.1:8848"

def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# 运行多个实例，只需要修改端口号，重新运行 python server.py 命令即可
port = int(os.getenv('OCR_SERVICE_PORT', 8091))
# 会自动获取本机ip地址
ip = get_ip()


@app.route("/")
def index():
    return render_template('index.html')
    
@app.route('/ocr', methods=['POST', 'GET'])
def detect():
    file = request.files['file']
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1]
        random_name = '{}.{}'.format(uuid.uuid4().hex, ext)
        savepath = os.path.join('caches', secure_filename(random_name))
        file.save(savepath)
        # time-1
        t1 = time.time()
        img = cv2.imread(savepath)
        img_result = ocr.ocr(img)
        # time-2
        t2 = time.time()

        '''
        识别结果将以列表返回在img_result，根据具体需求进行改写
        '''
        results = []
        print(len(img_result))

        for i in range(len(img_result)):
            print(len(img_result[i]))
            for j in range(len(img_result[i])):
                print(len(img_result[i][j]))
                results.append(img_result[i][j][1][0])
        print(results)
        return jsonify({
            '服务状态': 'success',
            '识别结果': results,
            '识别时间': '{:.4f}s'.format(t2-t1)
        })

    return jsonify({'服务状态': 'faild'})

def register_to_nacos():

    response = requests.post("http://127.0.0.1:8848/nacos/v1/ns/instance", data={
        "serviceName": "ocr-service",
        "groupName": "ocr_back",
        "ip": ip,
        "port": port,
        "namespaceId": "public",
        "weight": 1,
        "enabled": True,
        "ephemeral": True,
        "metadata": {},
        "clusterName": "",
        "service": "",
        "checksum": ""
    })
    if response.status_code == 200:
        print("Service registered successfully with Nacos")
    else:
        print(f"Failed to register service with Nacos: {response.text}")
def service_register_non_temporary():
    client = nacos.NacosClient("127.0.0.1:8848", namespace="public", username="nacos", password="nacos")
    client.add_naming_instance("ocr-service", "127.0.0.1", port, group_name="ocr_back")

def service_beat():
    nacos_server = "http://127.0.0.1:8848/"
    namespace = "public"
    service_name = "ocr-service"
    group_name = "ocr_back"


    data = {
        "serviceName": service_name,
        "groupName": group_name,
        "ip": ip,
        "port": port,
        "namespaceId": namespace,
        "weight": 1,
        "enabled": True,
        "ephemeral": False,
        "metadata": {},
        "clusterName": "",
        "service": "",
        "checksum": ""
    }
    while True:
        response = requests.put(f"{nacos_server}nacos/v1/ns/instance/beat", params=data, json=data)
        if response.status_code == 200:
            print("Heartbeat sent successfully to Nacos")
        else:
            print(f"Failed to send heartbeat to Nacos: {response.text}")
        time.sleep(5)




if __name__ == '__main__':
    ocr = PaddleOCR(use_angle_cls=True,use_gpu=False) # 查看README的参数说明
    register_to_nacos()  # 注册服务到Nacos
    threading.Thread(target=service_beat, daemon=True).start()  # Start heartbeat thread
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True, processes=1)
    '''
    app.run()中可以接受两个参数，分别是threaded和processes，用于开启线程支持和进程支持。
    1.threaded : 多线程支持，默认为False，即不开启多线程;
    2.processes：进程数量，默认为1.
    '''