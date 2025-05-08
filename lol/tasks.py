# lol/tasks.py
import datetime
import time
from celery import shared_task
import logging
from collections import deque

from lol.models import PatchVersion
from lol.services.riot_api import RiotApiService
from scripts.lol_api.get_summer_info import (
    get_match_detail,
    get_search_match_ids,
    get_summoner_info_v1,
    get_summoner_info_v2,
    get_summoner_info_v3,
)

logger = logging.getLogger(__name__)

version_time = datetime.datetime(2025, 4, 30, 3, 0, tzinfo=datetime.timezone.utc)


@shared_task
def fetch_summoner_puuids(start_page=1):
    ids = deque()

    try:
        puuid_list, have_next = get_summoner_info_v3()
        ids.extend(puuid_list)
        logger.info("get_summoner_info_v1 완료")
        print(ids)

        match_ids = get_search_match_ids(ids, version_time)
        logger.info(f"get_search_match_ids 완료")
        logger.info(f"match_ids_length: {len(match_ids)}, {match_ids[0]}")

        for match_id in match_ids:
            get_match_detail(match_id)

    except Exception as e:
        logger.error(f"Error fetching summoner puuid: {e}")
        raise e


@shared_task
def collect_match_data():
    logger.info(f"get_puuid_info 시작: {time.time()}")
    start_time = time.time()  # 시작 시간 기록
    RiotApiService().get_puuid_info()
    logger.info(
        f"get_puuid_info 완료: {time.time()}, 소요 시간: {time.time() - start_time:.2f}초"
    )

    # start_time = int(PatchVersion.objects.first().release_date.timestamp())
    # for puuid in puuid_list:
    #     logger.info(f"get_search_match_ids_by_puuid {puuid} 시작: {time.time()}")
    #     start_time_match_ids = time.time()  # 시작 시간 기록
    #     match_ids = riot_api_service.get_search_match_ids_by_puuid(puuid, start_time)
    #     logger.info(
    #         f"get_search_match_ids_by_puuid {puuid} 완료: {time.time()}, 소요 시간: {time.time() - start_time_match_ids:.2f}초"
    #     )

    #     logger.info(f"get_match_detail {puuid} 시작: {time.time()}")
    #     start_time_match_detail = time.time()  # 시작 시간 기록
    #     for match_id in match_ids:
    #         riot_api_service.get_match_detail(match_id)
    #     logger.info(
    #         f"get_match_detail {puuid} 완료: {time.time()}, 소요 시간: {time.time() - start_time_match_detail:.2f}초"
    #     )
