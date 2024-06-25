import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
import stt.returnzero_service as returnzero_service
import threading
import queue
import uuid
import time

stt = Blueprint('stt', __name__)

# .env 파일 로드
load_dotenv()

# 동시 요청 수를 관리하기 위한 큐와 변수
request_queue = queue.Queue()
MAX_CONCURRENT_REQUESTS = os.getenv("MAX_CONCURRENT_REQUESTS", 1)
lock = threading.Lock()


# 응답을 관리하기 위한 큐
class ResponseQueue:
    def __init__(self):
        self.responses = {}
        self.lock = threading.Lock()

    def put(self, request_id, response):
        with self.lock:
            self.responses[request_id] = response

    def get(self, request_id):
        with self.lock:
            return self.responses.pop(request_id, None)


response_queue = ResponseQueue()


def worker():
    while True:
        request_id, file = request_queue.get()
        try:
            status, response_data = returnzero_service.request_text(file)
            response_queue.put(request_id, (status, response_data))
        except Exception as e:
            response_queue.put(request_id, (500, str(e)))
        finally:
            request_queue.task_done()


# 작업자 스레드 생성 및 시작
for _ in range(MAX_CONCURRENT_REQUESTS):
    threading.Thread(target=worker, daemon=True).start()


@stt.route('/', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'text': 'Error: No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'text': 'Error: No selected file'}), 400

    if file:
        request_id = str(uuid.uuid4())
        request_queue.put((request_id, file))

        while True:
            response = response_queue.get(request_id)
            if response:
                status, response_data = response
                return jsonify({'text': response_data}), status
            time.sleep(0.1)
