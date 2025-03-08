# server/lol/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamCompositionViewSet

router = DefaultRouter()
router.register(r'team-compositions', TeamCompositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
