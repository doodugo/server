# server/lol/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Champion, PositionChampion, TeamComposition
from .serializers import ChampionSerializer, TeamCompositionSerializer
from docs.custom_docs import team_composition_list_docs
from django.core.cache import cache
from django.db.models import Prefetch


class TeamCompositionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TeamComposition model."""

    queryset = TeamComposition.objects.all()
    serializer_class = TeamCompositionSerializer

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "top__champion",
                "jungle__champion",
                "mid__champion",
                "adc__champion",
                "support__champion",
            )
        )
        champion_ids = self.get_champion_ids()
        return self.filter_team_compositions(queryset, champion_ids)

    def get_champion_ids(self):
        """챔피언 ID를 가져오는 함수."""
        return {
            "top": self.request.query_params.get("top"),
            "mid": self.request.query_params.get("mid"),
            "adc": self.request.query_params.get("adc"),
            "jungle": self.request.query_params.get("jug"),
            "support": self.request.query_params.get("sup"),
        }

    def filter_team_compositions(self, queryset, champion_ids):
        """챔피언 ID에 따라 팀 구성 필터링."""
        for role, champion_id in champion_ids.items():
            if champion_id:
                queryset = queryset.filter(**{f"{role}__champion_id": champion_id})
        return queryset

    @team_composition_list_docs
    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 50
        queryset = self.get_queryset().order_by("-pick_count", "-win_count")[:200]

        top_compositions = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(top_compositions, many=True)
        return paginator.get_paginated_response(serializer.data)


# TODO 언어를 쿠키에 넣고 체크 후 나라 별 챔피언 이름으로 정렬 기능
class ChampionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Champion model."""

    queryset = Champion.objects.order_by("name").prefetch_related(
        Prefetch(
            "positionchampion_set",
            queryset=PositionChampion.objects.only(
                "id", "champion_id", "position", "patch_id"
            )
            .select_related("patch")
            .filter(pick_count__gt=15),
        ),
    )
    serializer_class = ChampionSerializer

    def list(self, request, *args, **kwargs):
        cache_key = "champion_list"
        cache_data = cache.get(cache_key)

        if cache_data:
            return Response(cache_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 60 * 60 * 24)
        return Response(serializer.data)
