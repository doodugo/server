import os
import django
from bs4 import BeautifulSoup
from datetime import datetime
from django.db.models import F

from lol.models import AdCarryChampion, Champion, JungleChampion, Match, MidChampion, SupportChampion, Team, TeamComposition, TopChampion

def create_or_get_champion_by_name(name):
    """챔피언 생성 또는 조회"""
    champion, _ = Champion.objects.get_or_create(
        name=name,
        defaults={'image_url': ''}  # 임시로 빈 값
    )
    return champion

def process_match_data(row) -> tuple[Match, bool, str]:
    try:
        print('이거 안됨?')
        date = datetime.strptime(
            row.select_one('td:nth-child(1)').get_text().strip(),
            '%Y-%m-%d'
        ).date()
        patch = row.select_one('td:nth-child(2)').get_text().strip()
        blue_team_name = row.select_one('td:nth-child(3)').get_text().strip()
        red_team_name = row.select_one('td:nth-child(4)').get_text().strip()
        winner_name = row.select_one('td:nth-child(5)').get_text().strip()
        print('이건 왜 안됨?:', blue_team_name, red_team_name, winner_name)
        blue_team, _ = Team.objects.get_or_create(
            name=blue_team_name,
        )
        red_team, _ = Team.objects.get_or_create(
            name=red_team_name,
        )
        print(blue_team, red_team)
        winner = blue_team if winner_name == blue_team_name else red_team
        match, created = Match.objects.get_or_create(
            date=date,
            patch=patch,
            blue_team=blue_team,
            red_team=red_team,
            winner=winner,
        )
        winner_check = 'blue' if winner == blue_team else 'red'
        if created:
            print(f"Created match: {match}")
        else:
            print(f"Match already exists: {match}")
        return match, created, winner_check

    except AttributeError as e:
        print(f"HTML 파싱 오류: {e}")
        raise
    except ValueError as e:
        print(f"날짜 형식 오류: {e}")
        raise
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        raise

def create_role_champions(champions):
    """포지션별 챔피언 객체 생성"""
    role_objects = []
    role_classes = [TopChampion, JungleChampion, MidChampion, AdCarryChampion, SupportChampion]

    for champion, role_class in zip(champions, role_classes):
        champ = create_or_get_champion_by_name(champion)
        print(f"Creating {role_class.__name__} for {champ.name}")
        role_obj, _ = role_class.objects.get_or_create(champion=champ)
        role_objects.append(role_obj)

    return role_objects

def process_pick_data(row, winner_check):
    blue_champions = []
    red_champions = []

    blue_td = row.select_one('td:nth-child(8)')
    if blue_td:
        blue_spans = blue_td.find_all('span', title=True)
        print("Blue Team Champions:")
        for span in blue_spans:
            champion = create_or_get_champion_by_name(span['title'])
            blue_champions.append(champion)

    red_td = row.select_one('td:nth-child(9)')
    if red_td:
        red_spans = red_td.find_all('span', title=True)
        print("Red Team Champions:")
        for span in red_spans:
            champion = create_or_get_champion_by_name(span['title'])
            red_champions.append(champion)

    if blue_champions and red_champions:
        # 챔피언이 5명이 아닌 경우 에러 처리
        if len(blue_champions) != 5 or len(red_champions) != 5:
            print(f"Warning: Invalid team composition. Blue: {len(blue_champions)}, Red: {len(red_champions)}")
            assert False

        # 포지션별 챔피언 생성
        blue_role_objects = create_role_champions(blue_champions)
        red_role_objects = create_role_champions(red_champions)

        # 팀 구성 생성
        blue_team_composition, _ = TeamComposition.objects.get_or_create(
            top=blue_role_objects[0],
            jungle=blue_role_objects[1],
            mid=blue_role_objects[2],
            adc=blue_role_objects[3],
            support=blue_role_objects[4],
        )
        
        red_team_composition, _ = TeamComposition.objects.get_or_create(
            top=red_role_objects[0],
            jungle=red_role_objects[1],
            mid=red_role_objects[2],
            adc=red_role_objects[3],
            support=red_role_objects[4],
        )

        # 벌크 업데이트를 위해 F() 표현식 사용
        TeamComposition.objects.filter(id=blue_team_composition.id).update(
            pick_count=F('pick_count') + 1,
            win_count=F('win_count') + 1 if winner_check == 'blue' else F('win_count')
        )
        
        TeamComposition.objects.filter(id=red_team_composition.id).update(
            pick_count=F('pick_count') + 1,
            win_count=F('win_count') + 1 if winner_check == 'red' else F('win_count')
        )

    return blue_champions, red_champions
