from flask import Blueprint, request, jsonify
import asyncio
import stt.service as service

stt = Blueprint('stt', __name__)

@stt.route('/', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'message': 'Error: No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Error: No selected file'}), 400
    if file:
        file_contents = file.read()

        # 비동기 요청 처리
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status, response_data = loop.run_until_complete(service.request_text(file_contents))

        return jsonify({'message': response_data}), status
