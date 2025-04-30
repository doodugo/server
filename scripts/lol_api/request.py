import os
import requests
from collections import defaultdict
import time

RIOT_API_KEY = os.getenv("LOL_API_KEY")

REGION = 'kr'       # 소환사 API용 지역
MATCH_REGION = 'asia'  # 매치 API용 지역
TIER = 'EMERALD'
PAGE = 1
# https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/EMERALD/I?page=1&api_key=

headers = {
    "X-Riot-Token": RIOT_API_KEY
}

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

def get_summoner_info(summoner_name):
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{TIER}I?page={PAGE}&api_key={RIOT_API_KEY}"
    response = requests.get(url, headers=headers)
    print(response.json())



def get_emerald_summoners(queue='RANKED_SOLO_5x5', tier='EMERALD', division='I', page=1):
    url = f"https://{REGION}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}"
    response = requests.get(url, headers=headers)
    print('get_emerald_summoners', response.raise_for_status())
    return response.json()

def get_summoner_puuid(summoner_name):
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    response = requests.get(url, headers=headers)
    print('get_summoner_puuid', response.raise_for_status())
    return response.json()['puuid']

def get_match_ids(puuid, count=5):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    response = requests.get(url, headers=headers, params=params)
    print('get_match_ids', response.raise_for_status())
    return response.json()

def get_match_detail(match_id):
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=headers)
    print('get_match_detail', response.raise_for_status())
    return response.json()

def main():
    champion_stats = defaultdict(lambda: {"pick": 0, "win": 0})

    print("에메랄드 이상 소환사 목록 수집 중...")
    summoners = []
    for division in ['I', 'II', 'III', 'IV']:  # 에메랄드 IV ~ I
        for page in range(1, 3):  # 페이지 당 200명 정도, 2페이지만 예시로
            try:
                entries = get_emerald_summoners(division=division, page=page)
                summoners += [entry['summonerName'] for entry in entries]
                time.sleep(1)  # rate limit 보호
            except Exception as e:
                print(f"에러 발생 (division {division} page {page}): {e}")

    print(f"총 {len(summoners)}명의 소환사 수집 완료.")

    for idx, summoner_name in enumerate(summoners):
        try:
            puuid = get_summoner_puuid(summoner_name)
            match_ids = get_match_ids(puuid, count=5)

            for match_id in match_ids:
                match_data = get_match_detail(match_id)
                for participant in match_data['info']['participants']:
                    champ_name = participant['championName']
                    win = participant['win']

                    champion_stats[champ_name]['pick'] += 1
                    if win:
                        champion_stats[champ_name]['win'] += 1
            time.sleep(1)  # rate limit 보호

        except Exception as e:
            print(f"[{idx}] {summoner_name} 처리 중 에러: {e}")

    print("\n챔피언 통계 결과")
    sorted_stats = sorted(champion_stats.items(), key=lambda x: -x[1]['pick'])
    for champ, stats in sorted_stats:
        picks = stats['pick']
        wins = stats['win']
        win_rate = (wins / picks) * 100 if picks else 0
        print(f"{champ}: {picks} picks, {wins} wins, {win_rate:.2f}% win rate")

if __name__ == "__main__":
    main()
