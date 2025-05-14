from collections import defaultdict
import os
import time
from venv import logger
from django.db import transaction
from lol.models import (
    AdcSupportComposition,
    Champion,
    CounterRecord,
    Match,
    PatchVersion,
    Position,
    PositionChampion,
    TeamComposition,
    TopJungleMidComposition,
)
from lol.services.users import UserService
from utils.response import handle_api_response

RIOT_API_KEY = os.getenv("LOL_API_KEY")
TIERS = ["DIAMOND", "EMERALD", "PLATINUM"]
DIVISION = ["I", "II", "III", "IV"]
REGION = "kr"


class RiotApiService:
    def __init__(self):
        self.api_key = RIOT_API_KEY
        self.patch_version = PatchVersion.objects.first()
        self.start_time = int(self.patch_version.release_date.timestamp())

    def fetch_challenger_league_entries(self) -> dict:
        url = f"https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={self.api_key}"
        return handle_api_response(url)

    def fetch_grandmaster_league_entries(self) -> dict:
        url = f"https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={self.api_key}"
        return handle_api_response(url)

    def fetch_master_league_entries(self) -> dict:
        url = f"https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={self.api_key}"
        return handle_api_response(url)

    def fetch_league_entries(self, tier: str, division: str, page: int = 1) -> dict:
        """
        https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries
        205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
        limit: 10초마다 50개의 요청 챌린저, 마스터는 10초 30개 10분 500개
        """
        url = f"https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?api_key={self.api_key}&page={page}"
        return handle_api_response(url)

    def save_user_data(self, data, tier=None):
        if tier:
            tier = tier
        else:
            tier = data["tier"]
        UserService().save_user(
            puuid=data["puuid"],
            tier=tier,
            division=data["rank"],
            lp=data["leaguePoints"],
            wins=data["wins"],
            losses=data["losses"],
        )

    # TODO: 추후 endTime을 통해 데이터 범위 설정하기
    def get_match_ids_by_puuid(self, puuid: str) -> list[str]:
        """
        https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID
        uuid를 통해서 게임 id를 반환
        limit: 10초마다 2000개의 요청
        param:
            startTime: 시작시간, 종료시간, 대기줄(?), 유형(rank, normal, tourney, tutorial)
        startTime을 통해 해당 패치 기간 동안의 게임을 찾을 수 있음
        return:
            match_list: list[str] - match id 리스트
        """
        url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={self.start_time}&type=ranked&count=100&api_key={self.api_key}"
        return handle_api_response(url)

    def process_top_tier_league_entries(self):
        for url in [
            self.fetch_challenger_league_entries,
            self.fetch_master_league_entries,
            self.fetch_grandmaster_league_entries,
        ]:
            tier = None
            data = url()
            if data["tier"]:
                tier = data["tier"]

            for entry in data["entries"]:
                self.save_user_data(entry, tier)
                match_ids = self.get_match_ids_by_puuid(entry["puuid"])
                for match_id in match_ids:
                    self.get_match_detail(match_id)

    def process_grandmaster_league_entries(self):
        data = self.fetch_grandmaster_league_entries()
        for entry in data["entries"]:
            self.save_user_data(entry)
            match_ids = self.get_match_ids_by_puuid(entry["puuid"])
            for match_id in match_ids:
                self.get_match_detail(match_id)

    def process_middle_tier_user_data(self):
        for tier in TIERS:
            for division in DIVISION:
                page = 1
                while True:
                    try:
                        data_list = self.fetch_league_entries(tier, division, page)
                        if len(data_list) == 0:
                            break

                        for data in data_list:
                            self.save_user_data(data)
                            match_ids = self.get_match_ids_by_puuid(data["puuid"])
                            for match_id in match_ids:
                                self.get_match_detail(match_id)
                        page += 1
                    except Exception as e:
                        raise Exception(f"Error occurred during processing: tier={tier}, division={division}, page={page}") from e

    def handle_riot_api(self, url: str) -> dict:
        base_url = (
            f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/"
        )
        for tier in TIERS:
            for division in DIVISION:
                url_divide = f"{tier}/{division}"
                query_params = f"?page={page}&api_key={RIOT_API_KEY}"
                url = base_url + url_divide + query_params

                data_list = handle_api_response(url)
        return handle_api_response(url)

    def get_puuid_info(self, tier: str, division: str) -> dict:
        """
        205개가 날라오는 해당 region의 tier안에 있는 유저들의 정보 puuid를 가져와서 match들을 참조하고 가공
        limit: 10초마다 50개의 요청
        챌린저, 마스터는 10초 30개 10분 500개
        https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries
        """

        base_url = (
            f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/"
        )
        page = 1
        url_divide = f"{tier}/{division}"
        query_params = f"?api_key={RIOT_API_KEY}"
        page_params = f"&page={page}"
        url = base_url + url_divide + query_params + page_params

        while True:
            data_list = handle_api_response(url)
            if len(data_list) == 0:
                break
            for data in data_list:
                puuid_list = []
                for data in data_list:
                    UserService().save_user(
                        puuid=data["puuid"],
                        tier=data["tier"],
                        division=data["rank"],
                        lp=data["leaguePoints"],
                        wins=data["wins"],
                        losses=data["losses"],
                    )

                    puuid = data["puuid"]
                    start_time = int(
                        PatchVersion.objects.first().release_date.timestamp()
                    )
                    match_list = self.get_search_match_ids_by_puuid(
                        puuid,
                        start_time,
                    )

                    for match_id in match_list:
                        self.get_match_detail(match_id)

        # while True를 통해서 추 후 page 처리
        # if len(response.json()) == 205:
        #     page += 1
        # else:
        #     break

        return puuid_list

    def get_search_match_ids_by_puuid(self, puuid: str, start_time: int) -> list[str]:
        """
        https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID
        /lol/match/v5/matches/by-puuid/{puuid}/ids
        uuid를 통해서 게임 id를 반환
        limit: 10초마다 2000개의 요청
        param:
            startTime: 시작시간, 종료시간, 대기줄(?), 유형(rank, normal, tourney, tutorial)
        startTime을 통해 해당 패치 기간 동안의 게임을 찾을 수 있을 듯
        return:
            match_list: list[str] - match id 리스트
        """
        base_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/"
        query_params = f"{puuid}/ids?startTime={start_time}&type=ranked&count=20&api_key={RIOT_API_KEY}"
        url = base_url + query_params
        logger.info(f"get_search_match_ids_by_puuid {puuid} 시작: {time.time()}")
        match_list = handle_api_response(url)

        return match_list

    def fetch_match_detail(self, match_id: str) -> dict:
        base_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/"
        query_params = f"{match_id}?api_key={self.api_key}"
        url = base_url + query_params
        return handle_api_response(url)

    def get_match_detail(self, match_id: str) -> dict:
        """
        https://developer.riotgames.com/apis#match-v5/GET_getMatch
        /lol/match/v5/matches/{matchId}
        """
        logger.info(f"get_match_detail 시작 {match_id}")

        region = match_id.split("_")[0]
        match_number = match_id.split("_")[1]
        if Match.objects.filter(match_id=match_number, region=region).exists():
            logger.info(f"중복 데이터 {match_id}")
            return

        match_data = self.fetch_match_detail(match_id)
        data = match_data["info"]
        if not data:
            raise Exception(f"match_data: {match_data}, match_id: {match_id}")

        position_champion_dict = defaultdict(list)

        blue_win = data["teams"][0]["win"]  # blue_team
        with transaction.atomic():
            for participant in data["participants"]:

                champion_id = participant["championId"]
                champion = Champion.objects.get(id=champion_id)

                position = participant["teamPosition"]
                if position == "":
                    return
                champion_obj = self.transform_position_champion_obj(position, champion)
                position_champion_dict[position].append(champion_obj)

            blue_compositions = self.get_or_create_compositions(
                position_champion_dict, 0
            )
            red_compositions = self.get_or_create_compositions(
                position_champion_dict, 1
            )

            self.update_composition_stats(blue_compositions, blue_win)
            self.update_composition_stats(red_compositions, not blue_win)
            self.process_counter_data(position_champion_dict, blue_win)

            self.create_match(match_number, region, blue_compositions, red_compositions)

            logger.info(f"get_match_detail 처리 완료 {match_id}")

    def process_counter_data(self, position_champion_dict, blue_win):
        for position in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]:
                record, _ = CounterRecord.get_or_create_record(
                    self.patch_version,
                    position,
                    position_champion_dict[position][0].champion,
                    position_champion_dict[position][1].champion,
                )
                if blue_win:
                    record.wins_a += 1
                else:
                    record.wins_b += 1
                record.save()

    def get_or_create_compositions(self, position_champion_dict, team_idx):
        return {
            "TOP": position_champion_dict["TOP"][team_idx],
            "JUNGLE": position_champion_dict["JUNGLE"][team_idx],
            "MIDDLE": position_champion_dict["MIDDLE"][team_idx],
            "BOTTOM": position_champion_dict["BOTTOM"][team_idx],
            "UTILITY": position_champion_dict["UTILITY"][team_idx],
            "team": TeamComposition.objects.get_or_create(
                patch=self.patch_version,
                top=position_champion_dict["TOP"][team_idx],
                jungle=position_champion_dict["JUNGLE"][team_idx],
                mid=position_champion_dict["MIDDLE"][team_idx],
                adc=position_champion_dict["BOTTOM"][team_idx],
                support=position_champion_dict["UTILITY"][team_idx],
            )[0],
            "top_jungle_mid": TopJungleMidComposition.objects.get_or_create(
                patch=self.patch_version,
                top=position_champion_dict["TOP"][team_idx],
                jungle=position_champion_dict["JUNGLE"][team_idx],
                mid=position_champion_dict["MIDDLE"][team_idx],
            )[0],
            "adc_support": AdcSupportComposition.objects.get_or_create(
                patch=self.patch_version,
                adc=position_champion_dict["BOTTOM"][team_idx],
                support=position_champion_dict["UTILITY"][team_idx],
            )[0],
        }

    def update_composition_stats(self, compositions: dict, is_win):
        """조합의 승/패에 따른 통계를 갱신합니다."""
        for composition in compositions.values():
            composition.pick_count += 1
            if is_win:
                composition.win_count += 1
            composition.save()

    def create_match(self, match_number, region, blue_compositions, red_compositions):
        """매치 정보를 생성합니다."""
        return Match.objects.create(
            match_id=match_number,
            region=region,
            blue_team=blue_compositions["team"],
            red_team=red_compositions["team"],
        )

    def handle_match_processing(
        self, position_champion_dict, match_number, region, blue_win
    ):
        """매치 데이터를 처리하여 저장합니다."""
        blue_compositions = self.get_or_create_compositions(position_champion_dict, 0)
        red_compositions = self.get_or_create_compositions(position_champion_dict, 1)
        self.update_composition_stats(blue_compositions, blue_win)
        self.update_composition_stats(red_compositions, not blue_win)
        return self.create_match(
            match_number, region, blue_compositions, red_compositions
        )

    def transform_position_champion_obj(self, position: str, Champion: Champion) -> str:
        if position == "TOP":
            return PositionChampion.objects.get_or_create(
                patch=self.patch_version,
                champion=Champion,
                position=Position.TOP,
            )[0]
        elif position == "JUNGLE":
            return PositionChampion.objects.get_or_create(
                patch=self.patch_version,
                champion=Champion,
                position=Position.JUNGLE,
            )[0]
        elif position == "MIDDLE":
            return PositionChampion.objects.get_or_create(
                patch=self.patch_version,
                champion=Champion,
                position=Position.MID,
            )[0]
        elif position == "BOTTOM":
            return PositionChampion.objects.get_or_create(
                patch=self.patch_version,
                champion=Champion,
                position=Position.ADC,
            )[0]
        elif position == "UTILITY":
            return PositionChampion.objects.get_or_create(
                patch=self.patch_version,
                champion=Champion,
                position=Position.SUPPORT,
            )[0]
        else:
            raise Exception(f"handle_position_obj 오류 {position}, {Champion}")

    def handle_champion_str(self, position: str) -> str:
        if position == "TOP":
            return Position.TOP
        elif position == "JUNGLE":
            return Position.JUNGLE
        elif position == "MIDDLE":
            return Position.MID
        elif position == "BOTTOM":
            return Position.ADC
        elif position == "UTILITY":
            return Position.SUPPORT
