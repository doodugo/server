import requests
from bs4 import BeautifulSoup

url = "https://lol.fandom.com/wiki/LCK/2025_Season/Cup/Match_History"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 모든 tr 요소를 찾고
rows = soup.select('table tbody tr', class_='mhgame-blue multirow-highlighter')

# 각 tr에서 8번째와 9번째 td의 span title 속성값 추출
for row in rows:
    # 8번째 td (블루팀)
    blue_td = row.select_one('td:nth-child(8)')
    if blue_td:
        blue_spans = blue_td.find_all('span', title=True)
        print("Blue Team:")
        for span in blue_spans:
            print(f"  {span['title']}")
    
    # 9번째 td (레드팀)
    red_td = row.select_one('td:nth-child(9)')
    if red_td:
        red_spans = red_td.find_all('span', title=True)
        print("Red Team:")
        for span in red_spans:
            print(f"  {span['title']}")
    print()

print(f"Total matches: {len(rows)}")
