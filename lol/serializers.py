from rest_framework import serializers
from .models import Champion, TeamComposition

class TeamCompositionSerializer(serializers.ModelSerializer):
    """Serializer for TeamComposition model."""
    
    class Meta:
        model = TeamComposition
        fields = '__all__'  # 모든 필드를 포함


class ChampionSerializer(serializers.ModelSerializer):
    """Serializer for Champion model."""
    
    class Meta:
        model = Champion
        fields = ['id', 'name', 'name_ko', 'image_url']
