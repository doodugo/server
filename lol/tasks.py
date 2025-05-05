# lol/tasks.py
import datetime
from celery import shared_task
import logging
from collections import deque

from scripts.lol_api.get_summer_info import get_match_detail, get_search_match_ids, get_summoner_info_v1, get_summoner_info_v2, get_summoner_info_v3

logger = logging.getLogger(__name__)

version_time = datetime.datetime(2025, 4, 30, 3, 0, tzinfo=datetime.timezone.utc)

@shared_task
def fetch_summoner_puuids(start_page = 1):
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

