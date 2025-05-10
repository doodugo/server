import os
import django
from bs4 import BeautifulSoup
from datetime import datetime
from django.db.models import F

from lol.models import AdCarryChampion, Champion, JungleChampion, EsportsGame, MidChampion, SupportChampion, Team, TeamComposition, TopChampion

from scripts.transform_map import transform_map

def create_or_get_champion_by_name(name):
    """챔피언 생성 또는 조회"""
    name = name.lower()
    name = transform_map.get(name, name)
    try:
        champion = Champion.objects.get(
            name=name,
        )
    except Champion.DoesNotExist:
        print(f"Champion {name} does not exist")
        raise
    return champion

def process_match_data(row) -> tuple[EsportsGame, bool, str]:
    try:
        print('process_match_data 시작')
        date = datetime.strptime(
            row.select_one('td:nth-child(1)').get_text().strip(),
            '%Y-%m-%d'
        ).date()
        patch = row.select_one('td:nth-child(2)').get_text().strip()

        blue_team_td = row.select_one('td:nth-child(3)')
        blue_team_name = blue_team_td.select_one('a').get('title').replace('std', '').strip()
        red_team_td = row.select_one('td:nth-child(4)')
        red_team_name = red_team_td.select_one('a').get('title').replace('std', '').strip()
        winner_td = row.select_one('td:nth-child(5)')
        winner_name = winner_td.select_one('a').get('title').replace('std', '').strip()

        blue_team, _ = Team.objects.get_or_create(
            name=blue_team_name,
        )
        red_team, _ = Team.objects.get_or_create(
            name=red_team_name,
        )
        print('팀 디버깅:', blue_team, red_team)

        winner = blue_team if winner_name == blue_team_name else red_team

        blue_td = row.select_one('td:nth-child(8)')
        red_td = row.select_one('td:nth-child(9)')

        blue_team_composition, red_team_composition = process_pick_data(blue_td, red_td)
        print('process_pick_data 종료')

        match, created = EsportsGame.objects.get_or_create(
            date=date,
            patch=patch,
            blue_team=blue_team,
            red_team=red_team,
            winner=winner,
            blue_composition=blue_team_composition,
            red_composition=red_team_composition,
        )

        if created:
            print(f"Created match: {match}")
            blue_team_composition.pick_count = F('pick_count') + 1
            red_team_composition.pick_count = F('pick_count') + 1
            if winner == blue_team:
                blue_team_composition.win_count = F('win_count') + 1
            else:
                red_team_composition.win_count = F('win_count') + 1
            blue_team_composition.save()
            red_team_composition.save()
        else:
            print(f"Match already exists: {match}")
        return match, created

    except AttributeError as e:
        print(f"HTML 파싱 오류: {e}")
        raise
    except ValueError as e:
        print(f"날짜 형식 오류: {e}")
        raise
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        raise

def create_role_champions(champions_obj):
    """포지션별 챔피언 객체 생성"""
    role_objects = []
    role_classes = [TopChampion, JungleChampion, MidChampion, AdCarryChampion, SupportChampion]

    for champion_obj, role_class in zip(champions_obj, role_classes):
        role_obj, _ = role_class.objects.get_or_create(champion=champion_obj)
        role_objects.append(role_obj)

    return role_objects

def process_pick_data(blue_td, red_td):
    blue_champions = []
    red_champions = []

    if blue_td:
        blue_spans = blue_td.find_all('span', title=True)
        for span in blue_spans:
            champion_obj = create_or_get_champion_by_name(span['title'])
            blue_champions.append(champion_obj)

    if red_td:
        red_spans = red_td.find_all('span', title=True)
        for span in red_spans:
            champion_obj = create_or_get_champion_by_name(span['title'])
            red_champions.append(champion_obj)

    if blue_champions and red_champions:
        if len(blue_champions) != 5 or len(red_champions) != 5:
            print(f"Warning: Invalid team composition. Blue: {len(blue_champions)}, Red: {len(red_champions)}")
            assert False

        # 포지션별 챔피언 생성
        blue_role_objects = create_role_champions(blue_champions)
        red_role_objects = create_role_champions(red_champions)

        # 팀 구성 생성
        print('팀 구성 생성 시작')
        blue_team_composition, _ = TeamComposition.objects.get_or_create(
            top=blue_role_objects[0],
            jungle=blue_role_objects[1],
            mid=blue_role_objects[2],
            adc=blue_role_objects[3],
            support=blue_role_objects[4],
        )
        print('Blue Team Composition:', blue_team_composition)
        red_team_composition, _ = TeamComposition.objects.get_or_create(
            top=red_role_objects[0],
            jungle=red_role_objects[1],
            mid=red_role_objects[2],
            adc=red_role_objects[3],
            support=red_role_objects[4],
        )

        # 벌크 업데이트를 위해 F() 표현식 사용

    return blue_team_composition, red_team_composition
