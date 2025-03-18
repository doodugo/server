from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter

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
    ]
)
