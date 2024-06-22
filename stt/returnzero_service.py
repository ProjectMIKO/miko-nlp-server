import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

import json
import requests
import aiohttp
import asyncio

async def request_text(file):
    client_id = os.getenv("RT_CLIENT_ID")
    client_secret = os.getenv("RT_CLIENT_SECRET")

    # 인증 요청
    auth_resp = requests.post(
        'https://openapi.vito.ai/v1/authenticate',
        data={
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    auth_resp.raise_for_status()
    accessToken = auth_resp.json()['access_token']
    print(f"Access Token: {accessToken}")

    config = {
        "use_diarization": True,
        "diarization": {"spk_count": 5},
        "use_itn": False,
        "use_disfluency_filter": False,
        "use_profanity_filter": False,
        "use_paragraph_splitter": True,
        "paragraph_splitter": {"max": 50}
    }

    # 전사 요청 제출
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        data = aiohttp.FormData()
        data.add_field('config', json.dumps(config))
        data.add_field('file', file.stream, filename=file.filename, content_type=file.content_type)

        async with session.post(
            'https://openapi.vito.ai/v1/transcribe',
            headers={'Authorization': 'bearer ' + accessToken},
            data=data
        ) as resp:
            resp.raise_for_status()
            response_json = await resp.json()
            transcription_id = response_json['id']
            print(f"Transcription ID: {transcription_id}")

        # 전사 상태 확인
        status_url = f'https://openapi.vito.ai/v1/transcribe/{transcription_id}'
        while True:
            async with session.get(
                status_url,
                headers={'Authorization': 'bearer ' + accessToken}
            ) as status_resp:
                print(f"Checking status at URL: {status_url}")
                status_resp.raise_for_status()
                status_data = await status_resp.json()
                print(f"Status Data: {status_data}")

                if status_data['status'] == 'completed':
                    return status_resp.status, status_data['results']
                elif status_data['status'] == 'failed':
                    return status_resp.status, "Transcription failed"
                else:
                    await asyncio.sleep(5)
