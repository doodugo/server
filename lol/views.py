# server/lol/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import TeamComposition
from .serializers import TeamCompositionSerializer

class TeamCompositionViewSet(viewsets.ModelViewSet):
    """ViewSet for TeamComposition model."""
    queryset = TeamComposition.objects.all()
    serializer_class = TeamCompositionSerializer

    def list(self, request, *args, **kwargs):

        top_champion_id = request.query_params.get('top')
        mid_champion_id = request.query_params.get('mid')
        adc_champion_id = request.query_params.get('adc')
        jungle_champion_id = request.query_params.get('jung')
        support_champion_id = request.query_params.get('sup')

        queryset = TeamComposition.objects.all()


        if top_champion_id:
            queryset = queryset.filter(top__champion_id=top_champion_id)
        if mid_champion_id:
            queryset = queryset.filter(mid__champion_id=mid_champion_id)
        if adc_champion_id:
            queryset = queryset.filter(adc__champion_id=adc_champion_id)
        if jungle_champion_id:
            queryset = queryset.filter(jungle__champion_id=jungle_champion_id)
        if support_champion_id:
            queryset = queryset.filter(support__champion_id=support_champion_id)

        top_compositions = queryset.order_by('-pick_count', '-win_count')[:3]

        serializer = self.get_serializer(top_compositions, many=True)
        return Response(serializer.data)
