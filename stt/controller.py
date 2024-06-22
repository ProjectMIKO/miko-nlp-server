from flask import Blueprint, request, jsonify
import asyncio
import stt.service as etri_service
import stt.returnzero_service as returnzero_service

stt = Blueprint('stt', __name__)

async def call_service(service_function, file):
    return await service_function(file)

@stt.route('/', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'text': 'Error: No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'text': 'Error: No selected file'}), 400
    if file:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        status, response_data = loop.run_until_complete(call_service(returnzero_service.request_text, file))

        return jsonify({'text': response_data}), status
