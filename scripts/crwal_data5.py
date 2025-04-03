# docker compose run --rm app sh -c "python scripts/crwal_data5.py"
import requests
from bs4 import BeautifulSoup
import os


# url = "https://lol.fandom.com/wiki/LCK/2025_Season/Cup/Match_History"
# url = input('url: ')
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')
import os
import sys
import django
from django.conf import settings
# docker-compose run --rm app sh -c "python manage.py runserver 0.0.0.0:8000"
# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
sys.path.insert(0, server_dir)

# Django 설정을 먼저 로드
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
django.setup()

# Django 설정이 로드된 후에 임포트
from scripts.add_data import process_match_data, process_pick_data
from scripts.transform_map import transform_map
# 설정이 제대로 로드됐는지 확인 (선택사항)
if not settings.configured:
    raise RuntimeError("Django settings are not configured properly")


from scripts.transform_map import match_history_url
from django.db import transaction
for url in match_history_url:
    '''
        atomic을 추가함으로 무결성 보장
        match를 통해 중복 로직 처리 방지
    '''

    with transaction.atomic():
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 특정 클래스를 가진 테이블의 tbody 선택
        table = soup.select_one('table.wikitable.hoverable-multirows.mhgame.sortable.plainlinks')
        if table:
            rows = table.select('tbody tr')
        else:
            raise ValueError(f"Table not found in {url}")
        for row in rows[3:]:
            if row.get('class') == ['mhgame-blue']:
                continue
            # 날짜
            date_td = row.select_one('td:nth-child(1)')
            match_id_td = row.select_one('td:nth-child(6)')
            match, created = process_match_data(row)
            if not created:
                break
            print(f"Total matches: {len(rows)}")

