import requests
from bs4 import BeautifulSoup
import os


url = "https://lol.fandom.com/wiki/LCK/2025_Season/Cup/Match_History"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
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

# 설정이 제대로 로드됐는지 확인 (선택사항)
if not settings.configured:
    raise RuntimeError("Django settings are not configured properly")

# 특정 클래스를 가진 테이블의 tbody 선택
table = soup.select_one('table.wikitable.hoverable-multirows.mhgame.sortable.plainlinks')
if table:
    rows = table.select('tbody tr')
else:
    rows = []

print(len(rows))
for row in rows[3:4]:
    if row.get('class') == ['mhgame-blue']:
        continue
    # 날짜
    date_td = row.select_one('td:nth-child(1)')
    match_id_td = row.select_one('td:nth-child(6)')
    match, created, winner_check = process_match_data(row)

    if created:
        blue_champions, red_champions = process_pick_data(row, winner_check)

    # TODO 플레이어 추가
    # # 플레이어 (a 태그 텍스트 추출)
    # blue_team_player = row.select_one('td:nth-child(10)')
    # if blue_team_player:
    #     player_links = blue_team_player.find_all('a', class_='catlink-players')
    #     print("Blue Team Players:")
    #     for link in player_links:
    #         print(f"  {link.get_text()}")  # a 태그 안의 텍스트만 추출

    # red_team_player = row.select_one('td:nth-child(11)')
    # if red_team_player:
    #     player_links = red_team_player.find_all('a', class_='catlink-players')
    #     print("Red Team Players:")
    #     for link in player_links:
    #         print(f"  {link.get_text()}")  # a 태그 안의 텍스트만 추출

print(f"Total matches: {len(rows)}")
