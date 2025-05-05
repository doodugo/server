import os
import requests
from collections import defaultdict
import time
import logging

logger = logging.getLogger(__name__)

RIOT_API_KEY = os.getenv("LOL_API_KEY")

REGION = "kr"  # 소환사 API용 지역
MATCH_REGION = "asia"  # 매치 API용 지역
# TIERS = ['EMERALD', 'DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'IRON']
TIERS = ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]

PAGE = 1
DIVISION = ["I", "II", "III", "IV"]

headers = {"X-Riot-Token": RIOT_API_KEY}

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
}


def get_summoner_info_v1() -> tuple[list[str], bool]:
    """
    205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
    limit: 10초마다 50개의 요청
    챌린저, 마스터는 10초 30개 10분 500개
    """
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{TIERS[0]}/I?page={PAGE}&api_key={RIOT_API_KEY}"
    response = requests.get(url)
    print(response.status_code)
    print("response.json()", response.json())
    ids = []
    for summoner in response.json():
        ids.append(summoner["puuid"])

    have_next = True
    if len(ids) != 205:
        have_next = False

    return ids, have_next


def get_summoner_info_v3() -> tuple[list[str], bool]:
    """ 
    205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
    limit: 10초마다 50개의 요청
    챌린저, 마스터는 10초 30개 10분 500개
    https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries
    """
    ids = []
    for division in DIVISION[:2]:
        url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{TIERS[0]}/{division}?page={PAGE}&api_key={RIOT_API_KEY}"
        response = requests.get(url)
        temp_list = []
        for data in response.json():
            temp_list.append(data['puuid'])

        ids.extend(temp_list)

    have_next = True
    if len(ids) != 205:
        have_next = False

    return ids, have_next


def get_summoner_info_v2(page=1) -> tuple[list[str], bool]:
    """
    205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
    limit: 10초마다 50개의 요청
    챌린저, 마스터는 10초 30개 10분 500개
    """

    ids = []
    request_count = 0
    RATE_LIMIT = 50
    RATE_WINDOW = 10
    last_request_time = time.time()

    for tier in TIERS:
        for division in DIVISION:
            while True:
                url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}&api_key={RIOT_API_KEY}"

                request_count += 1
                if request_count >= RATE_LIMIT:
                    elapsed = time.time() - last_request_time
                    if elapsed < RATE_WINDOW:
                        time.sleep(RATE_WINDOW - elapsed)
                    request_count = 0
                    last_request_time = time.time()

                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    logger.error(
                        f"[{tier} {division}] 오류 코드: {response.status_code}, {response.text}"
                    )
                    raise Exception(f"API 오류: {response.status_code}")

                new_ids = [summoner["puuid"] for summoner in response.json()]
                logger.info(
                    f"[{tier} {division}] 페이지 {page}에서 {len(new_ids)}개의 puuid 수집"
                )

                if len(new_ids) == 0 or len(new_ids) != 205:
                    break

                ids.extend(new_ids)
            page += 1
            logger.info(f"[{tier} {division}] page {page}, 누적 수집: {len(ids)}")


def get_search_match_ids(puuid_q, datetime_obj):
    """
    https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID
    /lol/match/v5/matches/by-puuid/{puuid}/ids
    uuid를 통해서 게임 id를 반환
    limit: 10초마다 2000개의 요청
    param:
        startTime: 시작시간, 종료시간, 대기줄(?), 유형(rank, normal, tourney, tutorial)
    startTime을 통해 해당 패치 기간 동안의 게임을 찾을 수 있을 듯

    """
    start_time = int(datetime_obj.timestamp())
    match_id_list = []
    request_count = 0
    RATE_LIMIT = 1999  # 10초마다 허용되는 최대 요청 수
    RATE_WINDOW = 10
    start_time = int(datetime_obj.timestamp())

    for puuid in puuid_q:
        url = (
            f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/"
            f"{puuid}/ids?startTime={start_time}&count=20&api_key={RIOT_API_KEY}"
        )

        print(url)

        for attempt in range(3):
            response = requests.get(url)
            if response.status_code == 200:
                print(f"success, {response.json()}")
                match_id_list.extend(response.json())
                break
            elif response.status_code == 429:
                print(f"429, time to sleep")
                time.sleep(RATE_WINDOW)
                continue
            else:
                logger.error(f"[{puuid}] 오류 코드: {response.status_code}, {response.text}")
                print(response.text)
                raise Exception(f"API 오류: {response.status_code}, {response.text}")

    return match_id_list


def get_match_detail(match_id_list):
    """
    /lol/match/v5/matches/{matchId}
    https://developer.riotgames.com/apis#match-v5/GET_getMatch
    디테일: https://developer.riotgames.com/apis#match-v5/GET_getTimeline
    match_id를 통해 게임 정보를 반환
    gameVersion 게임버젼
    limit: 10초마다 2000개의 요청

    데이터 가공
    """
    for match_id in match_id_list[:3]:
        url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
        response = requests.get(url)
        print(response.json(), url)

        data = response.json()["info"]
        for p in data["participants"]:
            champion_id = p["championId"]
            k, d, a = p["kills"], p["deaths"], p["assists"]

            print(
                champion_id,
                p["championName"],
                p["role"],
                p["win"],
                p["individualPosition"],
                p["lane"],
            )


def get_puuid_by_name_tag(name, tag):
    url = f"https://{MATCH_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={RIOT_API_KEY}"
    response = requests.get(url, headers=headers)
    print(response.json())
    return response.json()


if __name__ == "__main__":
    # get_summoner_info()
    # _csF-gaO_znp0cPQuz5aCpMIn7etFyQcVWmLIOHOAgyorCNNdjbPGBay6NE0YH44GXY_W1o0r0qmXQ

    # match_ids = get_search_match_ids('QPnXtzmq1lCLgV7Y_ucmIipuuuhsfXpY8OXiDVT8Hk6aF-Tu9swRK_Y2fAlQ0UyCldvpOKpgwD4PkQ')
    # get_match_detail(match_ids[0])
    # get_puuid_by_name_tag('왕의등장', 'kr1')
    get_match_detail("KR_7619479517")
    # 왕의등장 puuid: c5fBITtF86VyyejWp0ie70dhix_MmlvdP4T_n9Yffni8YQIM4ZOEaPc7Caufifmstz1wgKkhannfjw
# KR_7619479517

import datetime

# UTC 기준의 datetime 객체
dt = datetime.datetime(2025, 3, 1, 0, 0, tzinfo=datetime.timezone.utc)

# UTC 기준 에폭 타임스탬프
timestamp = int(dt.timestamp())
print(timestamp)
