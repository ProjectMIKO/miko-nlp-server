from flask import Blueprint, request, jsonify
import nlp_keyword.service as service

keyword = Blueprint('nlp_keyword', __name__)


@keyword.route('/', methods=['POST'])
def get_keyword():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        keyword, subtitle, cost = service.process_message(user_message)
        print(f"키워드: {keyword}")
        # print(f"소제목: {subtitle}")
        return jsonify({"keyword": keyword, "subtitle": subtitle, "cost": cost}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
