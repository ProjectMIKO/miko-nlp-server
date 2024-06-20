from openai import OpenAI
from config.openai import OPENAI_API_KEY
from util.cost_calculator import calculate_cost

client = OpenAI(api_key=OPENAI_API_KEY)

def process_message(user_message):
    # GPT 모델에 요약 요청
    prompt = f"다음 회의 내용을 하나의 키워드로 요약해줘:\n\n{user_message}\n\n하나의 키워드:"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion)
    response_message = chat_completion.choices[0].message.content.strip()

    print(f"요청 내용: \n{user_message}")
    # gpt 요청 비용 계산
    cost = calculate_cost(chat_completion)
    print(f"Cost: ${cost:.5f}")

    return response_message, cost
