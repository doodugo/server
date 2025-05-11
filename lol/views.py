# server/lol/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Champion, PositionChampion, TeamComposition
from .serializers import (
    ChampionSerializer,
    PositionChampionSerializer,
    TeamCompositionSerializer,
)
from docs.custom_docs import team_composition_list_docs
from django.core.cache import cache
from django.db.models import Prefetch
from django.db.models import Q


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
        return self.filter_queryset(queryset)

    def get_champion_ids(self):
        """챔피언 ID를 가져오는 함수."""
        query_dict = dict()
        if self.request.query_params.get("top"):
            query_dict["top"] = self.request.query_params.get("top")
        if self.request.query_params.get("mid"):
            query_dict["mid"] = self.request.query_params.get("mid")
        if self.request.query_params.get("adc"):
            query_dict["adc"] = self.request.query_params.get("adc")
        if self.request.query_params.get("jug"):
            query_dict["jungle"] = self.request.query_params.get("jug")
        if self.request.query_params.get("sup"):
            query_dict["support"] = self.request.query_params.get("sup")
        return query_dict

    def get_exclude_champion_ids(self):
        """제외할 챔피언 ID를 가져오는 함수."""
        return self.request.query_params.getlist("exclude")

    def filter_queryset(self, queryset):
        """챔피언 ID에 따라 팀 구성 필터링."""
        champion_ids = self.get_champion_ids()
        exclude_champion_ids = self.get_exclude_champion_ids()
        if champion_ids:
            for role, champion_id in champion_ids.items():
                if champion_id:
                    queryset = queryset.filter(**{f"{role}__champion_id": champion_id})

        if exclude_champion_ids:
            queryset = queryset.exclude(
                Q(top__champion_id__in=exclude_champion_ids)
                | Q(jungle__champion_id__in=exclude_champion_ids)
                | Q(mid__champion_id__in=exclude_champion_ids)
                | Q(adc__champion_id__in=exclude_champion_ids)
                | Q(support__champion_id__in=exclude_champion_ids)
            )

        if champion_ids or exclude_champion_ids:
            return queryset[:3]

        return queryset.order_by("-pick_count", "-win_count")[:200]

    @team_composition_list_docs
    def list(self, request, *args, **kwargs):
        """
        파라미터를 넣지 않으면 모든 챔피언 조합을 페이지네이션 해서 반환 \n
        파라미터를 넣으면 특정 챔피언 조합 조회 api로 사용
        """
        paginator = PageNumberPagination()
        paginator.page_size = 50
        queryset = self.get_queryset()

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


class PositionChampionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for PositionChampion model."""

    queryset = PositionChampion.objects.all()
    serializer_class = PositionChampionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("champion").order_by(
            "-pick_count", "-win_count"
        )
        return queryset
