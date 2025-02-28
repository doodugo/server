import requests
from bs4 import BeautifulSoup

url = "https://lol.fandom.com/wiki/LCK/2025_Season/Cup/Match_History"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# XPath에 해당하는 요소 찾기
td_elements = soup.select('tr td:nth-child(8) span')  # 8번째 td에서 span들 선택

# 첫 번째부터 다섯 번째 span의 title 속성값 출력
for i in range(5):
    if i < len(td_elements):
        print(td_elements[i].get('title'))
