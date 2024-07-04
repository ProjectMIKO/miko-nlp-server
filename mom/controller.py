import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
import mom.service as service
import asyncio

mom = Blueprint('mom', __name__)

# .env 파일 로드
load_dotenv()


@mom.route('/', methods=['POST'])
def get_mom():
    try:
        print("\nGPT MOM 요청 시작")
        data = request.json

        conversations = data.get('conversations', [])
        vertexes = data.get('vertexes', [])

        # 메시지 구성
        user_message = ' '.join([f"speaker({conv['user']}): {conv['script']}" for conv in conversations])
        vertex_message = ' '.join([f"vertex({vertex['keyword']}): {vertex['subject']}" for vertex in vertexes])

        combined_message = f"{user_message} {vertex_message}"
        print(f"combined_message: {combined_message}")

        if not combined_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        # 비동기 서비스 호출
        meeting_notes, cost = asyncio.run(service.process_message(combined_message))
        print(f"회의록: {meeting_notes}")
        print(f"요청 비용: ${cost:.5f}")

        response = {
            "mom": meeting_notes,
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"에러: {str(e)}")
        return jsonify({"error": str(e)}), 500
