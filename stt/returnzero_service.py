import os
from dotenv import load_dotenv
import json
import requests
import time
import threading

# .env 파일 로드
load_dotenv()

access_token = None
token_expiry_time = None
token_lock = threading.Lock()


def get_access_token():
    global access_token, token_expiry_time
    with token_lock:
        if access_token and token_expiry_time and time.time() < token_expiry_time:
            return access_token

    client_id = os.getenv("RT_CLIENT_ID")
    client_secret = os.getenv("RT_CLIENT_SECRET")
    auth_resp = requests.post(
        'https://openapi.vito.ai/v1/authenticate',
        data={
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    print("\n리턴제로 토큰 재발급")
    auth_resp.raise_for_status()
    access_token = auth_resp.json()['access_token']
    token_expiry_time = time.time() + 3600 * 6  # assuming token is valid for 6 hour
    return access_token


def request_text(file, max_retries=3):
    print("\n리턴제로 요청 시작")

    retries = 0
    while retries <= max_retries:
        try:
            access_token = get_access_token()

            config = {
                'domain': 'GENERAL',
                "use_diarization": False,
                "use_itn": True,
                "use_disfluency_filter": False,
                "use_profanity_filter": False,
                "use_paragraph_splitter": False,
                "paragraph_splitter": {"max": 50}
            }

            file.seek(0)
            files = {
                'config': (None, json.dumps(config), 'application/json'),
                'file': ("audio.wav", file.read(), "audio/wav")
            }

            transcribe_resp = requests.post(
                'https://openapi.vito.ai/v1/transcribe',
                headers={'Authorization': 'bearer ' + access_token},
                files=files

            )
            transcribe_resp.raise_for_status()
            response_json = transcribe_resp.json()
            transcription_id = response_json['id']

            status_url = f'https://openapi.vito.ai/v1/transcribe/{transcription_id}'
            timeout = time.time() + 10  # 10 sec from now
            while True:
                if time.time() > timeout:
                    raise Exception("Transcription request timed out")

                status_resp = requests.get(
                    status_url,
                    headers={'Authorization': 'bearer ' + access_token}
                )
                status_resp.raise_for_status()
                status_data = status_resp.json()
                print(f"Status Data: {status_data}")

                if status_data['status'] == 'completed':
                    script = ' '.join([utterance['msg'] for utterance in status_data['results']['utterances']])
                    return status_resp.status_code, script
                elif status_data['status'] == 'failed':
                    return status_resp.status_code, "Transcription failed"
                else:
                    time.sleep(1)

        except requests.RequestException as e:
            if e.response is not None:
                status_code = e.response.status_code
                error_code = e.response.json().get('code', 'Unknown error code')

                if status_code == 400:
                    print(f'잘못된 파라미터 요청: {error_code}')
                    return status_code, f"Bad request: {error_code}"

                elif status_code == 401:
                    print(f'유효하지 않은 토큰: {error_code}')
                    return status_code, f"Unauthorized: {error_code}"

                elif status_code == 403:
                    print(f'권한 없음: {error_code}')
                    return status_code, f"Forbidden: {error_code}"

                elif status_code == 404:
                    print(f'전사 결과 없음: {error_code}')
                    retries += 1
                    if retries > max_retries:
                        return status_code, f"Not found: {error_code}"
                    print(f"Retrying... ({retries}/{max_retries})")
                    time.sleep(1)  # 짧은 지연 후 재시도

                elif status_code == 410:
                    print(f'전사 결과 만료됨: {error_code}')
                    return status_code, f"Gone: {error_code}"

                elif status_code == 429:
                    print(f'요청 제한 초과: {error_code}')
                    return status_code, f"Too many requests: {error_code}"

                elif status_code == 500:
                    print(f'서버 오류: {error_code}')
                    return status_code, f"Server error: {error_code}"

                else:
                    print(f'Unexpected status code {status_code}: {error_code}')
                    return status_code, f"Unexpected error: {error_code}"

            else:
                print(f'Request error: {str(e)}')
                return 500, f"Request error: {str(e)}"

        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return 500, f"Unexpected error: {str(e)}"
