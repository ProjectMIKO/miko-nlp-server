from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost
import json
import aiohttp

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_message(user_message):
    print("\nGPT 키워드 요청 시작")
    # GPT 모델에 요약 요청
    prompt = f"""
            You are a meeting summarization bot. Your main task is to read the conversation, generate a very short title as a keyword, and summarize the content into key points under the corresponding topics.
            Here is an example of a conversation and the desired output format:
            
            Example conversation:
            "준호: 봇을 만들고 있는데 프롬포트를 더 다듬어주라. 윤아: 프롬포트를 어떻게 수정하고 싶어? 준호: 사용자에게 더 명확하게 지시할 수 있도록 하고 싶어. 민수: 그래, 사용자가 이해하기 쉽게 간결하게 쓰는게 중요하지. 윤아: 맞아, 너무 길면 오히려 혼란스러울 수 있어."
            
            Desired JSON output:
            {{
              "keyword": "봇 프롬포트 수정 회의",
              "summary": "봇 프롬포트 수정:\\n- 프롬포트를 더 다듬어달라는 요청\\n- 사용자에게 명확한 지시를 위한 수정 필요성 언급\\n- 간결하고 이해하기 쉽게 작성할 필요성 강조"
            }}
            
            Conversation to summarize:
            "{user_message}"
            """

    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a meeting summarization bot."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
    )

    response_message = json.loads(chat_completion.choices[0].message.content.strip())

    keyword = response_message.get("keyword")
    subtitle = response_message.get("summary")

    # print(f"요청 내용: \n{user_message}")
    # gpt 요청 비용 계산
    cost = calculate_cost(chat_completion)
    # print(f"키워드: {keyword}")
    # print(f"소제목: {subtitle}")
    # print(f"Cost: ${cost:.5f}")

    return keyword, subtitle, cost
