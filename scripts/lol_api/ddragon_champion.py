# docker compose run app python /app/scripts/lol_api/ddragon_champion.py
import requests

from setup_django import *
from lol.models import PatchVersion, Champion


def get_champion_information(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json"
    response = requests.get(url)
    data = response.json()["data"]
    for info in data.values():
        champion_id = info["key"]
        champion_name = info["id"]
        full_image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_name}_0.jpg"
        square_image_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_name}.png"
        Champion.objects.get_or_create(
            id=champion_id,
            name=champion_name,
            name_ko=info["name"],
            full_image_url=full_image_url,
            icon_image_url=square_image_url,
        )
        print(champion_id, champion_name)


if __name__ == "__main__":
    version = PatchVersion.objects.order_by("-id").first()
    get_champion_information(version.version)
