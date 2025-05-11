from rest_framework import serializers
from .models import Champion, LoLUser, Position, PositionChampion, TeamComposition


class LoLUserSerializer(serializers.ModelSerializer):
    """Serializer for LoLUser model."""

    class Meta:
        model = LoLUser
        fields = "__all__"


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
            "id",
            "top_champion",
            "jungle_champion",
            "mid_champion",
            "adc_champion",
            "support_champion",
            "pick_count",
            "win_count",
        ]

    def get_champion_info(self, position):
        """Helper method to return champion info as a dictionary."""
        if position and position.champion:
            return {
                "id": position.champion.id,
                "name": position.champion.name,
                "name_local": position.champion.name_ko,
                "full_image_url": position.champion.full_image_url,
                "icon_image_url": position.champion.icon_image_url,
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

    name_local = serializers.CharField(source="name_ko")
    positions = serializers.SerializerMethodField()

    class Meta:
        model = Champion
        fields = [
            "id",
            "name",
            "name_local",
            "full_image_url",
            "icon_image_url",
            "positions",
        ]

    def get_positions(self, obj):
        # Prefetched 데이터를 직접 사용
        position_map = {
            Position.TOP: "top",
            Position.JUNGLE: "jug",
            Position.MID: "mid",
            Position.ADC: "adc",
            Position.SUPPORT: "sup",
        }

        # positionchampion_set이 이미 Prefetch로 로드됨
        positions = {
            position_map[pos.position]
            for pos in obj.positionchampion_set.all()
            if pos.position in position_map
        }

        return list(positions)


class PositionChampionSerializer(serializers.ModelSerializer):
    """Serializer for PositionChampion model."""

    champion_name_ko = serializers.SerializerMethodField()
    champion_icon_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PositionChampion
        fields = [
            "champion_name_ko",
            "position",
            "pick_count",
            "win_count",
            "win_rate",
            "champion_icon_image_url",
        ]

    def get_champion_name_ko(self, obj):
        return obj.champion.name_ko

    def get_champion_icon_image_url(self, obj):
        return obj.champion.icon_image_url
