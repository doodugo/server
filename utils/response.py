import os
import time
import requests
from venv import logger

LIMIT_TIME = int(os.getenv("LIMIT_TIME", 10))


def handle_api_response(url):
    for _ in range(3):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            time.sleep(2)
        elif response.status_code == 429:
            logger.info(f"limit: url: {url}, status_code: {response.status_code}, text: {response.text}")
            time.sleep(LIMIT_TIME)
    raise Exception(
        f"Error: url: {url}, status_code: {response.status_code}, text: {response.text}"
    )
