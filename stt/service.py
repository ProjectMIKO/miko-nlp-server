import aiohttp
import base64
from config import ETRI_API_KEY

openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = ETRI_API_KEY
languageCode = "korean"


async def request_text(voice):
    audio_contents = base64.b64encode(voice).decode("utf8")

    request_json = {
        "argument": {
            "language_code": languageCode,
            "audio": audio_contents
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                openApiURL,
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Authorization": accessKey
                },
                json=request_json
        ) as response:
            response_data = await response.json()
            return response.status, response_data['return_object']['recognized']
