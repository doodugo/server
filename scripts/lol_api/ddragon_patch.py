# docker compose run app python /app/scripts/lol_api/ddragon_patch.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from setup_django import *
from lol.models import PatchVersion


# 최신 버전 정보를 가져오는 함수
def get_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    return response.json()[:3]  # 최신 버전 반환


# 주어진 버전으로 패치 노트 URL 생성
def get_patch_url(version):
    version_parts = version.split(".")
    patch_url = f"https://www.leagueoflegends.com/ko-KR/news/game-updates/patch-{int(version_parts[0]) + 10}-{"0" + version_parts[1]}-notes/"
    return patch_url


# 패치 노트 페이지에서 시간 정보 추출하는 함수
def get_patch_datetime(version):
    patch_url = get_patch_url(version)
    print(patch_url)
    response = requests.get(patch_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # 제공된 CSS 선택자를 사용하여 time 요소 찾기
        time_element = soup.select_one(
            "#__next > div > main > div > div > span:nth-child(3) > section > div.sc-6bee9aac-0.ieyshm.width-medium > div > div.metadata-with-links > div.metadata > time"
        )

        if time_element:
            # datetime 속성 값 추출
            datetime_value = time_element["datetime"]
            return datetime_value
        else:
            print(f"패치 노트에서 날짜를 찾을 수 없습니다: {version}")
            return None
    else:
        print(f"패치 노트를 찾을 수 없습니다: {version}")
        return None


# 버전 정보와 해당 패치 날짜를 가져오는 함수
def get_version_and_patch_datetime():
    version_list = get_version()
    for version in version_list:
        patch_datetime = get_patch_datetime(version)  # 해당 버전의 날짜 정보
        PatchVersion.objects.get_or_create(version=version, release_date=patch_datetime)
    return version_list, patch_datetime


if __name__ == "__main__":
    version, patch_datetime = get_version_and_patch_datetime()

    if patch_datetime:
        print(f"Patch Release Date for Version {version}: {patch_datetime}")
        dt = datetime.strptime(patch_datetime, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )

    else:
        print("Failed to retrieve patch datetime.")

if __name__ == "__main__":
    get_version_and_patch_datetime()
