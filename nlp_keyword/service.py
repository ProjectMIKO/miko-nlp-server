from openai import OpenAI
from config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def process_message(user_message):
    # GPT 모델에 요약 요청
    prompt = f"다음 회의 내용을 json 형식으로 keyword: 키워드를 1개 추출하고 subtitle: 소제목을 만들어줘:\n\n{user_message}\n\n"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    
    response_message = json.loads(chat_completion.choices[0].message.content.strip())

    keyword = response_message.get("keyword")
    subtitle = response_message.get("subtitle")

    print(f"요청 내용: \n{user_message}")
    # gpt 요청 비용 계산
    cost = calculate_cost(chat_completion)
    print(f"키워드: {keyword}")
    print(f"소제목: {subtitle}")
    print(f"Cost: ${cost:.5f}")

    return keyword, subtitle, cost
