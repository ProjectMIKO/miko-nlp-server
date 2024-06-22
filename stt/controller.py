
from flask import Blueprint, request, jsonify
import stt.returnzero_service as returnzero_service

stt = Blueprint('stt', __name__)

@stt.route('/', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'text': 'Error: No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'text': 'Error: No selected file'}), 400
    if file:
        try:
            status, response_data = returnzero_service.request_text(file)
            return jsonify({'text': response_data}), status
        except Exception as e:
            return jsonify({'text': str(e)}), 500
