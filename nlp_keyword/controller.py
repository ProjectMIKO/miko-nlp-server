from flask import Blueprint, request, jsonify
import nlp_keyword.service as service

keyword = Blueprint('nlp_keyword', __name__)


@keyword.route('/', methods=['POST'])
def get_keyword():
    try:
        print("\n키워드 요청 시작")
        data = request.json
        print(f"요청 데이터: {data}")

        # conversations에서 user와 content 추출 및 문자열 결합
        conversations = data.get('conversations', {})
        messages = []
        for conv_id, conv_list in conversations.items():
            for message in conv_list:
                user = message.get('user', '')
                content = message.get('content', '')
                combined_message = f"speaker({user}): {content}."
                messages.append(combined_message)

        # 모든 메시지를 하나의 문자열로 결합
        user_message = ' '.join(messages)

        if not user_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        keyword, subtitle, cost = service.process_message(user_message)
        print(f"키워드: {keyword}")
        # print(f"소제목: {subtitle}")
        return jsonify({"keyword": keyword, "subtitle": subtitle, "cost": cost}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
