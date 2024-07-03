from flask import Blueprint, request, jsonify
import nlp_keyword.service as service
import asyncio

keyword = Blueprint('nlp_keyword', __name__)


@keyword.route('/', methods=['POST'])
def get_keyword():
    try:
        print("\n키워드 요청 시작")
        data = request.json
        # print(f"요청 데이터: {data}")

        conversations = data.get('conversations', {})
        messages = []
        for conv_id, conv_list in conversations.items():
            for message in conv_list:
                user = message.get('user', '')
                script = message.get('script', '')
                combined_message = f"speaker({user}): {script}/"
                messages.append(combined_message)

        # 모든 메시지를 하나의 문자열로 결합
        user_message = ' '.join(messages)
        print(f"user_message: {user_message}")

        if not user_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        # 비동기 서비스 호출
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        idea, cost = loop.run_until_complete(service.process_message(user_message))
        print(f"아이디어 리스트: {idea}")
        print(f"요청 비용: ${cost:.5f}")

        response = {
            "idea": idea,
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"에러: {str(e)}")
        return jsonify({"error": str(e)}), 500
