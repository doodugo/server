import os
import time


LIMIT_SECOND = os.getenv("LIMIT_SECOND", 10)


def handle_api_response(response):
    if response.status_code == 200:
        return True
    elif response.status_code == 429:
        time.sleep(LIMIT_SECOND)
        return False
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")
