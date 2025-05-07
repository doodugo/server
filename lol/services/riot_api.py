from collections import defaultdict
import os
from venv import logger
import requests
from django.db import transaction
from lol.models import (
    AdCarryChampion,
    AdcSupportComposition,
    Champion,
    ChampionStat,
    JungleChampion,
    Match,
    MidChampion,
    PatchVersion,
    Position,
    SupportChampion,
    TeamComposition,
    TopChampion,
    TopJungleMidComposition,
)
from lol.services.users import UserService
from utils.response import handle_api_response

RIOT_API_KEY = os.getenv("LOL_API_KEY")
# TIERS = ["DIAMOND", "EMERALD", "PLATINUM"]
TIERS = ["DIAMOND"]
DIVISION = ["I"]  # test용
# DIVISION = ["I", "II", "III", "IV"]
REGION = "kr"


class RiotApiService:
    def get_puuid_info(self) -> dict:
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

                data_list = handle_api_response(url)

                # while True를 통해서 추 후 page 처리
                # if len(response.json()) == 205:
                #     page += 1
                # else:
                #     break

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
                    puuid_list.append(data["puuid"])
                logger.info(f"save_user {data['tier']} {data['rank']}")
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
        query_params = (
            f"{puuid}/ids?startTime={start_time}&type=ranked&count=20&api_key={RIOT_API_KEY}"
        )
        url = base_url + query_params
        match_list = handle_api_response(url)

        return match_list

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

        base_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/"
        query_params = f"{match_id}?api_key={RIOT_API_KEY}"
        url = base_url + query_params

        match_data = handle_api_response(url)

        data = match_data["info"]
        if not data:
            raise Exception(f"match_data: {match_data}, url: {url}")

        position_champion_dict = defaultdict(list)
        position_champion_list = []
        champion_stat_list = []

        blue_win = data["teams"][0]["win"]  # blue_team
        with transaction.atomic():
            for participant in data["participants"]:

                if participant["teamPosition"] == "":
                    return

                champion_id = participant["championId"]
                champion = Champion.objects.get(id=champion_id)
                position = participant["teamPosition"]
                champion_obj = self.handle_position_obj(position, champion)
                position_champion_dict[position].append(champion_obj)
                champion_stat_list.append(champion)
                position_champion_list.append(champion_obj)

            print(champion_stat_list)
            print(position_champion_list)

            for champion in champion_stat_list[0:5]:
                champion_stat, _ = ChampionStat.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    champion=champion,
                    position=self.handle_champion_str(participant["teamPosition"]),
                )
                champion_stat.pick_count += 1
                if blue_win:
                    champion_stat.win_count += 1
                champion_stat.save()

            for champion in champion_stat_list[5:10]:
                champion_stat, _ = ChampionStat.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    champion=champion,
                    position=self.handle_champion_str(participant["teamPosition"]),
                )
                champion_stat.pick_count += 1
                if not blue_win:
                    champion_stat.win_count += 1
                champion_stat.save()

            blue_team_composition, _ = TeamComposition.objects.get_or_create(
                patch=PatchVersion.objects.first(),
                top=position_champion_dict["TOP"][0],
                jungle=position_champion_dict["JUNGLE"][0],
                mid=position_champion_dict["MIDDLE"][0],
                adc=position_champion_dict["BOTTOM"][0],
                support=position_champion_dict["UTILITY"][0],
            )
            blue_top_jungle_mid_composition, _ = (
                TopJungleMidComposition.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    top=position_champion_dict["TOP"][0],
                    jungle=position_champion_dict["JUNGLE"][0],
                    mid=position_champion_dict["MIDDLE"][0],
                )
            )
            blue_adc_support_composition, _ = (
                AdcSupportComposition.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    adc=position_champion_dict["BOTTOM"][0],
                    support=position_champion_dict["UTILITY"][0],
                )
            )

            if blue_win:
                blue_team_composition.win_count += 1
                blue_top_jungle_mid_composition.win_count += 1
                blue_adc_support_composition.win_count += 1

            blue_team_composition.pick_count += 1
            blue_team_composition.save()
            blue_top_jungle_mid_composition.pick_count += 1
            blue_top_jungle_mid_composition.save()
            blue_adc_support_composition.pick_count += 1
            blue_adc_support_composition.save()

            red_team_composition, _ = TeamComposition.objects.get_or_create(
                patch=PatchVersion.objects.first(),
                top=position_champion_dict["TOP"][1],
                jungle=position_champion_dict["JUNGLE"][1],
                mid=position_champion_dict["MIDDLE"][1],
                adc=position_champion_dict["BOTTOM"][1],
                support=position_champion_dict["UTILITY"][1],
            )
            red_top_jungle_mid_composition, _ = (
                TopJungleMidComposition.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    top=position_champion_dict["TOP"][1],
                    jungle=position_champion_dict["JUNGLE"][1],
                    mid=position_champion_dict["MIDDLE"][1],
                )
            )
            red_adc_support_composition, _ = (
                AdcSupportComposition.objects.get_or_create(
                    patch=PatchVersion.objects.first(),
                    adc=position_champion_dict["BOTTOM"][1],
                    support=position_champion_dict["UTILITY"][1],
                )
            )

            if not blue_win:
                red_team_composition.win_count += 1
                red_top_jungle_mid_composition.win_count += 1
                red_adc_support_composition.win_count += 1

            red_team_composition.pick_count += 1
            red_team_composition.save()
            red_top_jungle_mid_composition.pick_count += 1
            red_top_jungle_mid_composition.save()
            red_adc_support_composition.pick_count += 1
            red_adc_support_composition.save()

            match = Match.objects.create(
                match_id=match_number,
                region=region,
                blue_team=blue_team_composition,
                red_team=red_team_composition,
            )

            logger.info(f"get_match_detail 처리 완료 {match_id}")

    def handle_position_obj(self, position: str, Champion: Champion) -> str:
        if position == "TOP":
            return TopChampion.objects.get_or_create(champion=Champion)[0]
        elif position == "JUNGLE":
            return JungleChampion.objects.get_or_create(champion=Champion)[0]
        elif position == "MIDDLE":
            return MidChampion.objects.get_or_create(champion=Champion)[0]
        elif position == "BOTTOM":
            return AdCarryChampion.objects.get_or_create(champion=Champion)[0]
        elif position == "UTILITY":
            return SupportChampion.objects.get_or_create(champion=Champion)[0]
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
