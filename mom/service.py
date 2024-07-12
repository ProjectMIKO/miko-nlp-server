from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost
import tiktoken

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_message(messages):
    print("\nGPT 회의록 요청 시작")

    mom = []
    cost = 0.0

    # 메시지를 토큰 수 제한 내에서 분할
    chunks = split_message_into_chunks(messages, max_tokens=13000)

    # GPT 모델에 요약 요청
    for chunk in chunks:
        prompt = f""" You are a meeting summarization bot. Your main task is to read the conversation, generate a 
        detailed meeting note body in html format in korean. Do not use any information from the example conversation 
        in your output. Only use the information from the provided Conversation to summarize.:
    
        Example conversation:
        keyword(여행 계획): 여행 장소 및 관광지 회의 \n conversations: [speaker(준호): 우리 여행 가자. speaker(윤아): 
        어디로 가고 싶어? speaker(준호): 대구 혹은 대전으로 가자. speaker(윤아): 그럼 성심당과 식장산을 방문하자.]
        keyword(점심 식사): 점심 식사에 관한 회의 \n conversations: [speaker(준호): 점심 뭐 먹을까? speaker(민수): 난 치킨이나 피자. speaker(윤아): 난 
        국밥이나 냉면. speaker(준호): 가까운 한우곰탕 어때? speaker(민수): 좋아.]
    
        Desired Markdown output:
        <h2> 여행 계획 </h2>
        여행 장소 및 관광지 회의
        <ul>
            <li> 대구 혹은 대전으로 여행 </li>
            <li> 성심당과 식장산을 방문하기로 함 </li>
        </ul>
    
        <h2> 점심 식사 </h2>
        점심 식사에 관한 회의
        <ul>
            <li> 치킨, 피자, 국밥 등의 메뉴 </li>
            <li> 가까운 한우곰탕에서 먹기로 결정 </li>
        </ul>
    
        Conversation to summarize:
        "{chunk}"
        """
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a meeting summarization bot."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",
        )

        response_message = chat_completion.choices[0].message.content.strip()
        mom.append(response_message)
        # gpt 요청 비용 계산
        cost += calculate_cost(chat_completion)

    combined_mom = "\n\n".join(mom)

    return combined_mom, cost


def split_message_into_chunks(messages, max_tokens):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    chunks = []
    current_chunk = []
    current_length = 0

    for message in messages:
        message_length = len(enc.encode(message))

        if current_length + message_length > max_tokens:
            chunks.append("\n".join(current_chunk))
            current_chunk = [message]
            current_length = message_length
        else:
            current_chunk.append(message)
            current_length += message_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
