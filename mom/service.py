from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_message(combined_message):
    print("\nGPT 회의록 요청 시작")
    # GPT 모델에 요약 요청
    prompt = f""" You are a meeting summarization bot. Your main task is to read the conversation, generate a detailed meeting note in markdown format. 
    Here is an example of a conversation and the desired output format:

    Example conversation: "준호: 우리 여행 가자. 윤아: 어디로 가고 싶어? 준호: 대구나 대전 어때? 민수: 난 대전가서 성심당 갈래. 윤아: 성심당 괜찮네. 근데 나 배고파.
    준호: 그럼 점심 뭐 먹을까? 민수: 난 치킨이나 피자. 윤아: 난 국밥먹고싶어. 준호: 그럼 가까운 한우곰탕이나 먹으러가자. 민수: 그럼 그러자. 그럼 대전에서 어디 또 갈까?
    윤아: 식장산 야경이 유명하대. 식장산 가자."

    Desired Markdown output:
    ## 여행 계획
    - **주요 토픽**: 여행 장소 및 관광지 회의
    - **주요 내용**: 대구 혹은 대전으로 여행, 성심당과 식장산을 방문하기로 함

    ## 점심 식사
    - **주요 토픽**: 점심 식사에 관한 회의
    - **주요 내용**: 치킨, 피자, 국밥 등의 메뉴, 가까운 한우곰탕에서 먹기로 결정

    Conversation to summarize:
    "{combined_message}"
    """

    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a meeting summarization bot."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
    )

    response_message = chat_completion.choices[0].message.content.strip()

    # gpt 요청 비용 계산
    cost = calculate_cost(chat_completion)

    return response_message, cost
