import requests
import os

RIOT_API_KEY = os.getenv("LOL_API_KEY")

REGION = 'kr'       # 소환사 API용 지역
MATCH_REGION = 'asia'  # 매치 API용 지역

def get_puuid_by_name_tag(name, tag):
    url = f'https://{MATCH_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={RIOT_API_KEY}'
    response = requests.get(url)
    print(response.json())
    return response.json()


if __name__ == "__main__":
    get_puuid_by_name_tag('왕의등장', 'kr1')
