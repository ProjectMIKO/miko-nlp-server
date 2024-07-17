from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost
import json

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_message(user_message):
    print("\nGPT 키워드 요청 시작")
    # GPT 모델에 요약 요청
    conversation = """준호: 우리 여행 가자. 윤아: 어디로 가고 싶어? 준호: 대구나 대전 어때? 민수: 난 대전가서 성심당 갈래. 윤아: 성심당 괜찮네. 근데 나 배고파.
    준호: 그럼 점심 뭐 먹을까? 민수: 난 치킨이나 피자. 윤아: 난 국밥먹고싶어. 준호: 그럼 가까운 한우곰탕이나 먹으러가자. 민수: 그럼 그러자. 그럼 대전에서 어디 또 갈까?
    윤아: 식장산 야경이 유명하대. 식장산 가자."""

    prompt = f""" You are a meeting summarization bot. Your main task is to read the conversation, generate very 
    short titles as keywords (nouns), and summarize the content into key points under the corresponding topics. There 
    can be multiple main topics, and each main topic can have multiple subtopics with a vertex depth of up to 3 
    levels. Make sure to include all sub-levels even if they are empty lists. this is important you must include least
    two subtopics.

    Here is an example of a conversation and the desired output format:

    Example conversation: "{conversation}"

    Desired JSON output:
    {{
      "idea": [
        {{
          "main": {{
            "keyword": "여행 계획",
            "subject": "여행 장소 및 관광지 회의"
          }},
          "sub": [
            {{
              "keyword": "장소에 대한 회의",
              "subject": "부산 혹은 대전으로 여행",
              "sub": [
                {{
                  "keyword": "부산",
                  "subject": "부산의 명소 및 관광지",
                  "sub": [
                    {{
                      "keyword": "해운대",
                      "subject": "부산의 해운대",
                      "sub": []
                    }},
                    {{
                      "keyword": "바다",
                      "subject": "해운대에서 바다가 보고싶음",
                      "sub": []
                    }},
                    {{
                      "keyword": "서핑",
                      "subject": "해운대에서 서핑하고 싶음",
                      "sub": []
                    }}
                  ]
                }},
                {{
                  "keyword": "대전",
                  "subject": "대전의 명소 및 관광지",
                  "sub": []
                }}
              ]
            }},
            {{
              "keyword": "대전의 관광지 결정",
              "subject": "성심당과 식장산을 방문하기로 함",
              "sub": [
                {{
                  "keyword": "성심당",
                  "subject": "대전 성심당 빵집",
                  "sub": []
                }},
                {{
                  "keyword": "식장산",
                  "subject": "대전 식장산 전망대",
                  "sub": []
                }}
              ]
            }}
          ]
        }},
        {{
          "main": {{
            "keyword": "점심 식사",
            "subject": "점심 식사에 관한 회의"
          }},
          "sub": [
            {{
              "keyword": "메뉴에 대한 고민",
              "subject": "치킨, 피자, 국밥 등의 메뉴",
              "sub": [
                {{
                  "keyword": "치킨",
                  "subject": "점심 메뉴 치킨",
                  "sub": []
                }},
                {{
                  "keyword": "피자",
                  "subject": "점심 메뉴 피자",
                  "sub": []
                }},
                {{
                  "keyword": "국밥",
                  "subject": "점심 메뉴 국밥",
                  "sub": []
                }}
              ]
            }},
            {{
              "keyword": "점심 식사 결정",
              "subject": "가까운 한우곰탕에서 먹기로 결정",
              "sub": [
                {{
                  "keyword": "한우곰탕",
                  "subject": "한우곰탕 맛집 및 메뉴",
                  "sub": []
                }},
                {{
                  "keyword": "식당 위치",
                  "subject": "한우곰탕 식당의 위치 및 정보",
                  "sub": []
                }}
              ]
            }}
          ]
        }}
      ]
    }}

    Now, summarize the following conversation into the specified JSON format, ensuring each sub-level is included, even if they are empty lists:

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

    idea = response_message.get("idea", [])

    # print(f"요청 내용: \n{user_message}")
    # gpt 요청 비용 계산
    cost = calculate_cost(chat_completion)
    # print(f"키워드: {keyword}")
    # print(f"소제목: {subtitle}")
    # print(f"Cost: ${cost:.5f}")

    return idea, cost
