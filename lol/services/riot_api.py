import os
import requests

from lol.services.users import UserService
from utils.response import handle_api_response

RIOT_API_KEY = os.getenv("LOL_API_KEY")
TIERS = ["DIAMOND", "EMERALD", "PLATINUM"]
DIVISION = ["I", "II", "III", "IV"]
REGION = "kr"


class RiotApiService:
    def get_summoner_info(self) -> dict:
        """
        205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
        limit: 10초마다 50개의 요청
        챌린저, 마스터는 10초 30개 10분 500개
        https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries
        """

        base_url = (
            f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/"
        )
        for tier in TIERS:
            for division in DIVISION:
                page = 1
                url_divide = f"{tier}/{division}"
                query_params = f"?page={page}&api_key={RIOT_API_KEY}"
                url = base_url + url_divide + query_params

                response = requests.get(url)
                for _ in range(2):
                    if handle_api_response(response):
                        break

                # while True를 통해서 추 후 page 처리
                # if len(response.json()) == 205:
                #     page += 1
                # else:
                #     break

                data_list = response.json()
                puuid_list = []
                for data in data_list:
                    UserService.save_user(
                        puuid=data["puuid"],
                        tier=data["tier"],
                        division=data["rank"],
                        lp=data["leaguePoints"],
                        wins=data["wins"],
                        losses=data["losses"],
                    )
                    puuid_list.append(data["puuid"])
                match_ids = self.get_search_match_ids(puuid_list, datetime_obj)


    def get_search_match_ids(self, puuid_list: list[str], datetime_obj: datetime) -> list[str]:
        """
        https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID
        /lol/match/v5/matches/by-puuid/{puuid}/ids
        uuid를 통해서 게임 id를 반환
        limit: 10초마다 2000개의 요청
        param:
            startTime: 시작시간, 종료시간, 대기줄(?), 유형(rank, normal, tourney, tutorial)
        startTime을 통해 해당 패치 기간 동안의 게임을 찾을 수 있을 듯
        """

        base_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/"

        