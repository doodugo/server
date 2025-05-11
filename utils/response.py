import os
import time
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
from venv import logger

LIMIT_TIME = int(os.getenv("LIMIT_TIME", 10))


def handle_api_response(url):
    '''
        네트워크 에러가 가끔 발생해서 exception 추가
    '''
    for _ in range(3):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                time.sleep(2)
            elif response.status_code == 429:
                logger.info(
                    f"limit: url: {url}, status_code: {response.status_code}, text: {response.text}"
                )
                time.sleep(LIMIT_TIME)
            else:
                logger.error(
                    f"Unexpected response: url: {url}, status_code: {response.status_code}, text: {response.text}"
                )
        except (ConnectionError, Timeout, RequestException) as e:
            logger.error(f"Network error: url: {url}, error: {e}")
            time.sleep(LIMIT_TIME)

    raise Exception(
        f"Error: url: {url}, status_code: {response.status_code if 'response' in locals() else 'unknown'}, text: {response.text if 'response' in locals() else str(e)}"
    )
