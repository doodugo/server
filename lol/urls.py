# server/lol/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionChampionViewSet, TeamCompositionViewSet, ChampionViewSet

router = DefaultRouter()
router.register(r"team-compositions", TeamCompositionViewSet)
router.register(r"champions", ChampionViewSet)
router.register(r"position-champions", PositionChampionViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
