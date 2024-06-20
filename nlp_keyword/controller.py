from flask import Blueprint, request, jsonify
from nlp_keyword.service import process_message

keyword = Blueprint('nlp_keyword', __name__)

@keyword.route('/', methods=['POST'])
def get_keyword():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        keyword, subtitle, cost = process_message(user_message)

        return jsonify({"keyword": keyword, "subtitle": subtitle, "cost": cost}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
