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
        print("\nMOM 요청 시작")
        data = request.json

        conversations = {conv['_id']: conv for conv in data.get('conversations', [])}
        vertexes = data.get('vertexes', [])

        # 각 vertex에 대해 메시지를 구성
        messages = []
        # for vertex in vertexes:
        #     keyword = vertex['keyword']
        #     subject = vertex['subject']
        #     conversation_ids = vertex['conversationIds']
        #
        #     related_conversations = [f"speaker({conversations[cid]['user']}): {conversations[cid]['script']}" for cid in
        #                              conversation_ids]
        #     combined_conversations = " ".join(related_conversations)
        #
        #     message = f"keyword({keyword}): {subject} \n conversations: [{combined_conversations}]"
        #     messages.append(message)
        #
        # if not vertexes:
        #     message = f"keyword(없음): 없음 \n conversations: ["
        #     for conv_id, conversation in conversations.items():
        #         message += f"speaker({conversation['user']}): {conversation['script']} "
        #     message += "]"
        #     messages.append(message)
        for conv_id, conversation in conversations.items():
            message = f"speaker({conversation['user']}): {conversation['script']}"
            messages.append(message)

        # print(f"messages: {messages}")

        if not messages:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        # 비동기 서비스 호출
        meeting_notes, cost = asyncio.run(service.process_message(messages))
        print(f"회의록: {meeting_notes}")
        print(f"요청 비용: ${cost:.5f}")

        response = {
            "mom": meeting_notes,
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"에러: {str(e)}")
        return jsonify({"error": str(e)}), 500
