from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from lol.serializers import TeamCompositionSerializer

team_composition_list_docs = extend_schema(
    parameters=[
        OpenApiParameter(
            name="top",
            type=int,
            location=OpenApiParameter.QUERY,
            description="탑 챔피언 ID",
        ),
        OpenApiParameter(
            name="mid",
            type=int,
            location=OpenApiParameter.QUERY,
            description="미드 챔피언 ID",
        ),
        OpenApiParameter(
            name="adc",
            type=int,
            location=OpenApiParameter.QUERY,
            description="원딜 챔피언 ID",
        ),
        OpenApiParameter(
            name="jug",
            type=int,
            location=OpenApiParameter.QUERY,
            description="정글 챔피언 ID",
        ),
        OpenApiParameter(
            name="sup",
            type=int,
            location=OpenApiParameter.QUERY,
            description="서포터 챔피언 ID",
        ),
        OpenApiParameter(
            name="exclude",
            type={"type": "array", "items": {"type": "integer"}},
            location=OpenApiParameter.QUERY,
            description="제외할 챔피언 ID 리스트 (ex: ?exclude=1&exclude=2&exclude=3)",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=TeamCompositionSerializer,
            description="성공적으로 팀 구성 목록을 가져왔습니다.",
            examples=[
                OpenApiExample(
                    name="성공 예시",
                    description="팀 구성 목록을 반환하는 예시",
                    value={
                        "count": 200,
                        "next": "http://127.0.0.1:8000/api/lol/team-compositions/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 476,
                                "top_champion": {
                                    "id": 3,
                                    "name": "Galio",
                                    "name_local": "갈리오",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Galio_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Galio.png",
                                },
                                "jungle_champion": {
                                    "id": 5,
                                    "name": "XinZhao",
                                    "name_local": "신 짜오",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/XinZhao_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/XinZhao.png",
                                },
                                "mid_champion": {
                                    "id": 61,
                                    "name": "Orianna",
                                    "name_local": "오리아나",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Orianna_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Orianna.png",
                                },
                                "adc_champion": {
                                    "id": 145,
                                    "name": "Kaisa",
                                    "name_local": "카이사",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Kaisa_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Kaisa.png",
                                },
                                "support_champion": {
                                    "id": 89,
                                    "name": "Leona",
                                    "name_local": "레오나",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Leona_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Leona.png",
                                },
                                "pick_count": 2,
                                "win_count": 2,
                            },
                            {
                                "id": 561,
                                "top_champion": {
                                    "id": 126,
                                    "name": "Jayce",
                                    "name_local": "제이스",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Jayce_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Jayce.png",
                                },
                                "jungle_champion": {
                                    "id": 143,
                                    "name": "Zyra",
                                    "name_local": "자이라",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Zyra_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Zyra.png",
                                },
                                "mid_champion": {
                                    "id": 777,
                                    "name": "Yone",
                                    "name_local": "요네",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Yone_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Yone.png",
                                },
                                "adc_champion": {
                                    "id": 202,
                                    "name": "Jhin",
                                    "name_local": "진",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Jhin_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Jhin.png",
                                },
                                "support_champion": {
                                    "id": 12,
                                    "name": "Alistar",
                                    "name_local": "알리스타",
                                    "full_image_url": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Alistar_0.jpg",
                                    "icon_image_url": "https://ddragon.leagueoflegends.com/cdn/15.7.1/img/champion/Alistar.png",
                                },
                                "pick_count": 2,
                                "win_count": 1,
                            },
                        ],
                    },
                )
            ],
        ),
    },
)
