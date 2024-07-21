import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
import stt.returnzero_service as returnzero_service
import threading
import queue
import uuid
import time
import torchaudio
from util.converter import convert_to_wav
from stt.audio_processing.pre_processing import process_audio

stt = Blueprint('stt', __name__)

# .env 파일 로드
load_dotenv()

# 마지막 429 에러 시간을 추적하는 전역 변수와 딜레이 초기값
last_429_time = 0
current_delay = 5
max_delay = 60


def check_global_delay():
    global last_429_time, current_delay
    with lock:
        if last_429_time and time.time() - last_429_time < current_delay:
            print(f"waiting... {int(time.time() - last_429_time)}/{current_delay} sec")
            return True
    return False


def update_global_delay():
    global last_429_time, current_delay
    with lock:
        last_429_time = time.time()
        current_delay = min(current_delay + 5, max_delay)


# 동시 요청 수를 관리하기 위한 큐와 변수
request_queue = queue.Queue()
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 1))
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
        # 전역 지연 확인
        if check_global_delay():
            time.sleep(5)
            continue

        request_id, file_content = request_queue.get()
        try:
            # 파일을 wav로 변환
            wav_stream = convert_to_wav(file_content)

            # 메모리에서 torchaudio로 로드
            wav_stream.seek(0)
            waveform, sample_rate = torchaudio.load(wav_stream, format='wav')

            processed_waveform = process_audio(waveform, sample_rate)

            # 리턴제로 서비스 요청
            status, response_data = returnzero_service.request_text(processed_waveform, max_retries=3)

            # 429 에러 발생 시 요청을 다시 큐에 넣음
            if status == 429:
                update_global_delay()
                request_queue.put((request_id, file_content))
            else:
                response_queue.put(request_id, (status, response_data))

        except Exception as e:
            print(f"Error: {str(e)}")
            response_queue.put(request_id, (500, str(e)))
        finally:
            request_queue.task_done()


# 작업자 스레드 생성 및 시작
for _ in range(MAX_CONCURRENT_REQUESTS):
    threading.Thread(target=worker, daemon=True).start()


@stt.route('/', methods=['POST'])
def speech_to_text():
    global current_delay
    # 전역 지연 확인
    if check_global_delay():
        return jsonify({'text': 'Too many requests, please try again later.'}), 429

    if 'file' not in request.files:
        return jsonify({'text': 'Error: No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'text': 'Error: No selected file'}), 400

    if file:
        # 파일을 메모리에 임시 저장
        file_content = file.read()
        file.seek(0)

        request_id = str(uuid.uuid4())
        request_queue.put((request_id, file_content))

        while True:
            response = response_queue.get(request_id)
            if response:
                status, response_data = response
                if status == 429:
                    update_global_delay()
                else:
                    current_delay = 5
                    return jsonify({'text': response_data}), status
            time.sleep(0.1)
