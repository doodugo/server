import os
import sys
import django
from django.conf import settings
import requests


# docker compose run --rm app sh -c "python scripts/crwal_champion_data.py"
def create_champion_data(champions):
    for champion in champions:
        champion_obj, _ = Champion.objects.get_or_create(
            name=champion["key"].lower()
        )
        
        full_image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion['key']}_0.jpg"
        icon_image_url = f"https://ddragon.leagueoflegends.com/cdn/15.6.1/img/champion/{champion['key']}.png"
        
        champion_obj.name_ko = champion["name"]
        champion_obj.full_image_url = full_image_url
        champion_obj.icon_image_url = icon_image_url
        champion_obj.save()
        print(f"Champion {champion['name']} created")


url = "https://ddragon.leagueoflegends.com/cdn/15.6.1/data/ko_KR/champion.json"
response = requests.get(url)

current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
sys.path.insert(0, server_dir)
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
django.setup()
if not settings.configured:
    raise RuntimeError("Django settings are not configured properly")


from lol.models import Champion
if response.status_code == 200:
    data = response.json()
    champions = [{"key": key, "name": champion_data["name"]}
                for key, champion_data in data['data'].items()]
    create_champion_data(champions)
else:
    print(f"Failed to retrieve data: {response.status_code}")




