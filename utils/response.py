import logging
import os
import requests
import time
from requests.exceptions import ConnectionError, Timeout, RequestException
from urllib3.exceptions import NewConnectionError, MaxRetryError
import socket

LIMIT_TIME = int(os.getenv("LIMIT_TIME", 10))
logger = logging.getLogger(__name__)


def handle_api_response(url):
    """
    200과 429를 제외한 모든 에러에 대해 로그 기록 후 재시도
    """
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                logger.info(
                    f"[{attempt}/{max_retries}] Rate limit reached: {url}, status_code: {response.status_code}"
                )
                time.sleep(LIMIT_TIME)
                continue

            # 200, 429 이외의 상태 코드
            logger.error(
                f"[{attempt}/{max_retries}] Unexpected response: url: {url}, status_code: {response.status_code}, text: {response.text}"
            )
            time.sleep(LIMIT_TIME)

        # 모든 네트워크 관련 에러 핸들링
        except requests.RequestException as e:
            logger.error(
                f"[{attempt}/{max_retries}] Network error: url: {url}, error: {e}"
            )
            time.sleep(LIMIT_TIME)

        # DNS 해석 에러 핸들링
        except socket.gaierror as e:
            logger.error(
                f"[{attempt}/{max_retries}] DNS resolution error: url: {url}, error: {e}"
            )
            time.sleep(LIMIT_TIME)

    raise Exception(f"Error: url: {url}, reached max retries")
