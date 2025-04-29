import requests

def get_champion_information(version):
    url = f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'
    response = requests.get(url)
    data = response.json()['data']
    for champion, info in data.items():
        champion_id = info['key']
        champion_name = info['name']
        full_image_url = f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_name}_0.jpg'
        square_image_url = f'https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_name}.png'
        print(champion_id, champion_name)

def get_version():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(url)
    return response.json()[0]


if __name__ == "__main__":
    version = get_version()
    get_champion_information(version)

