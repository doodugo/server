from rest_framework import serializers
from .models import TeamComposition

class TeamCompositionSerializer(serializers.ModelSerializer):
    """Serializer for TeamComposition model."""
    
    class Meta:
        model = TeamComposition
        fields = '__all__'  # 모든 필드를 포함
