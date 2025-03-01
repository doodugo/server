import requests
from bs4 import BeautifulSoup

url = "https://lol.fandom.com/wiki/LCK/2025_Season/Cup/Match_History"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 특정 클래스를 가진 테이블의 tbody 선택
table = soup.select_one('table.wikitable.hoverable-multirows.mhgame.sortable.plainlinks')
if table:
    rows = table.select('tbody tr')
else:
    rows = []

print(len(rows))
print(rows[0])
print()

print(rows[1])
print()

print(rows[2])
print()

print(rows[3])
print()

print(rows[4])
print()

print(rows[5])
print()

# print(rows[6])
# print(rows[7])
# print(rows[8])
# for row in rows:
#     if row.get('class') == ['mhgame-blue']:
#         continue
#     # 날짜
#     date_td = row.select_one('td:nth-child(1)')
#     if date_td:
#         print(f"Date: {date_td.get_text()}")
    
#     # 패치
#     patch_td = row.select_one('td:nth-child(2)')
#     if patch_td:
#         print(f"Patch: {patch_td.get_text()}")

#     # 블루팀 (이미지 alt 속성 추출)
#     blue_team_td = row.select_one('td:nth-child(3)')
#     if blue_team_td:
#         blue_team_img = blue_team_td.select_one('a img')
#         if blue_team_img:
#             print(f"Blue Team: {blue_team_img.get('alt', '').replace('std', '')}")

#     # 레드팀 (이미지 alt 속성 추출)
#     red_team_td = row.select_one('td:nth-child(4)')
#     if red_team_td:
#         red_team_img = red_team_td.select_one('a img')
#         if red_team_img:
#             print(f"Red Team: {red_team_img.get('alt', '').replace('std', '')}")

#     winner_team_td = row.select_one('td:nth-child(5)')
#     if red_team_td:
#         red_team_img = red_team_td.select_one('a img')
#         if red_team_img:
#             print(f"Red Team: {red_team_img.get('alt', '').replace('std', '')}")

#     blue_team_ban = row.select_one('td:nth-child(6)')
#     if blue_team_ban:
#         blue_bans = blue_team_ban.find_all('span', title=True)
#         print("Blue Team Ban Champions:")
#         for span in blue_bans:
#             print(f"  {span['title']}")

#     red_team_ban = row.select_one('td:nth-child(7)')
#     if red_team_ban:
#         red_bans = red_team_ban.find_all('span', title=True)
#         print("Red Team Ban Champions:")
#         for span in red_bans:
#             print(f"  {span['title']}")

#     # 블루팀 챔피언
#     blue_td = row.select_one('td:nth-child(8)')
#     if blue_td:
#         blue_spans = blue_td.find_all('span', title=True)
#         print("Blue Team Champions:")
#         for span in blue_spans:
#             print(f"  {span['title']}")
    
#     # 레드팀 챔피언
#     red_td = row.select_one('td:nth-child(9)')
#     if red_td:
#         red_spans = red_td.find_all('span', title=True)
#         print("Red Team Champions:")
#         for span in red_spans:
#             print(f"  {span['title']}")
#     print()

#     # 플레이어 (a 태그 텍스트 추출)
#     blue_team_player = row.select_one('td:nth-child(10)')
#     if blue_team_player:
#         player_links = blue_team_player.find_all('a', class_='catlink-players')
#         print("Blue Team Players:")
#         for link in player_links:
#             print(f"  {link.get_text()}")  # a 태그 안의 텍스트만 추출

#     red_team_player = row.select_one('td:nth-child(11)')
#     if red_team_player:
#         player_links = red_team_player.find_all('a', class_='catlink-players')
#         print("Red Team Players:")
#         for link in player_links:
#             print(f"  {link.get_text()}")  # a 태그 안의 텍스트만 추출

# print(f"Total matches: {len(rows)}")
