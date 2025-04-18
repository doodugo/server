from rest_framework import serializers
from .models import Champion, TeamComposition

class TeamCompositionSerializer(serializers.ModelSerializer):
    """Serializer for TeamComposition model."""
    
    top_champion = serializers.SerializerMethodField()
    jungle_champion = serializers.SerializerMethodField()
    mid_champion = serializers.SerializerMethodField()
    adc_champion = serializers.SerializerMethodField()
    support_champion = serializers.SerializerMethodField()

    class Meta:
        model = TeamComposition
        fields = [
            'id',
            'top_champion',
            'jungle_champion',
            'mid_champion',
            'adc_champion',
            'support_champion',
            'pick_count',
            'win_count'
        ]

    def get_champion_info(self, position):
        """Helper method to return champion info as a dictionary."""
        if position and position.champion:
            return {
                'id': position.champion.id,
                'name': position.champion.name,
                'name_local': position.champion.name_ko,
                'full_image_url': position.champion.full_image_url,
                'icon_image_url': position.champion.icon_image_url,
            }
        return None

    def get_top_champion(self, obj):
        return self.get_champion_info(obj.top)

    def get_jungle_champion(self, obj):
        return self.get_champion_info(obj.jungle)

    def get_mid_champion(self, obj):
        return self.get_champion_info(obj.mid)

    def get_adc_champion(self, obj):
        return self.get_champion_info(obj.adc)

    def get_support_champion(self, obj):
        return self.get_champion_info(obj.support)


class ChampionSerializer(serializers.ModelSerializer):
    """Serializer for Champion model."""

    name_local = serializers.CharField(source='name_ko')
    positions = serializers.SerializerMethodField()

    class Meta:
        model = Champion
        fields = [
            'id', 'name', 'name_local', 
            'full_image_url', 'icon_image_url',
            'positions'
        ]

    def get_positions(self, obj):
        positions = []

        if hasattr(obj, 'top_champion'):
            positions.append('top')
        if hasattr(obj, 'jungle_champion'):
            positions.append('jug')
        if hasattr(obj, 'mid_champion'):
            positions.append('mid')
        if hasattr(obj, 'adc_champion'):
            positions.append('adc')
        if hasattr(obj, 'support_champion'):
            positions.append('sup')

        return positions

    class Meta:
        model = Champion
        fields = [
            'id', 'name', 'name_local', 
            'full_image_url', 'icon_image_url',
            'positions'
        ]

    def get_positions(self, obj):
        positions = []

        if hasattr(obj, 'top_champion'):
            positions.append('top')
        if hasattr(obj, 'jungle_champion'):
            positions.append('jug')
        if hasattr(obj, 'mid_champion'):
            positions.append('mid')
        if hasattr(obj, 'adc_champion'):
            positions.append('adc')
        if hasattr(obj, 'support_champion'):
            positions.append('sup')

        return positions
