from django import forms
from django.contrib import admin

from lol.models import (
    AdcSupportComposition,
    Champion,
    EsportsGame,
    LoLUser,
    Match,
    PatchVersion,
    PositionChampion,
    Team,
    TeamComposition,
    TopJungleMidComposition,
)
from django.utils.translation import gettext_lazy as _

class CustomAdminSite(admin.AdminSite):
    site_header = "My Custom Admin"
    site_title = "Admin Portal"
    index_title = "Welcome to My Admin"

# Custom AdminSite 인스턴스 생성
custom_admin_site = CustomAdminSite(name='custom_admin')
custom_admin_site.register(Champion)
custom_admin_site.register(PositionChampion)
custom_admin_site.register(TeamComposition)
custom_admin_site.register(EsportsGame)
custom_admin_site.register(Match)
custom_admin_site.register(AdcSupportComposition)

# Register your models here.
@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_ko")


class ChampionFilter(admin.SimpleListFilter):
    """Base class for champion filters in different positions"""

    title = _("Champion")  # Default title, will be overridden by subclasses
    parameter_name = (
        "champion"  # Default parameter name, will be overridden by subclasses
    )
    position_field = None  # Will be set by subclasses

    def lookups(self, request, model_admin):
        # Get distinct champions for this position
        position_field = self.position_field
        champion_field = f"{position_field}__champion"

        # Get all unique champions in this position from the filtered queryset
        champions = (
            model_admin.get_queryset(request)
            .values_list(f"{champion_field}__name", f"{champion_field}__name_ko")
            .distinct()
            .order_by(f"{champion_field}__name")
        )

        # Return as (value, display_name) tuples
        return [
            (name, f"{name_ko} ({name})" if name_ko else name)
            for name, name_ko in champions
        ]

    def queryset(self, request, queryset):
        if self.value():
            # Filter the queryset when a value is selected
            filter_param = {f"{self.position_field}__champion__name": self.value()}
            return queryset.filter(**filter_param)
        return queryset


class TopChampionFilter(ChampionFilter):
    """Filter for champions in top position"""

    title = _("Top Champion")
    parameter_name = "top_champion"
    position_field = "top"


class JungleChampionFilter(ChampionFilter):
    """Filter for champions in jungle position"""

    title = _("Jungle Champion")
    parameter_name = "jungle_champion"
    position_field = "jungle"


class MidChampionFilter(ChampionFilter):
    """Filter for champions in mid position"""

    title = _("Mid Champion")
    parameter_name = "mid_champion"
    position_field = "mid"


class AdcChampionFilter(ChampionFilter):
    """Filter for champions in ADC position"""

    title = _("ADC Champion")
    parameter_name = "adc_champion"
    position_field = "adc"


class SupportChampionFilter(ChampionFilter):
    """Filter for champions in support position"""

    title = _("Support Champion")
    parameter_name = "support_champion"
    position_field = "support"


@admin.register(PositionChampion)
class PositionChampionAdmin(admin.ModelAdmin):
    search_fields = ["champion__name_ko"]
    list_display = (
        "id",
        "champion_name_ko",
        "patch",
        "position",
        "pick_count",
        "win_count",
    )
    list_filter = ("position",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).order_by("-pick_count", "-win_count")
        qs = qs.select_related("champion", "patch")
        return qs

    def champion_name_ko(self, obj):
        return obj.champion.name_ko

    champion_name_ko.short_description = "챔피언 이름"

    def patch(self, obj):
        return obj.patch.version

    patch.short_description = "패치 버전"


admin.site.register(Match)


@admin.register(TeamComposition)
class TeamCompositionAdmin(admin.ModelAdmin):
    list_display = (
        "top_champion_name",
        "jungle_champion_name",
        "mid_champion_name",
        "adc_champion_name",
        "support_champion_name",
        "pick_count",
        "win_count",
    )
    list_filter = ("patch",)

    autocomplete_fields = ["top", "jungle", "mid", "adc", "support"]

    search_fields = [
        "top__champion__name_ko",
        "jungle__champion__name_ko",
        "mid__champion__name_ko",
        "adc__champion__name_ko",
        "support__champion__name_ko",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "patch",
            "top__champion",
            "jungle__champion",
            "mid__champion",
            "adc__champion",
            "support__champion",
        ).order_by("-pick_count", "-win_count")
        return qs

    def top_champion_name(self, obj):
        return obj.top.champion.name_ko

    def jungle_champion_name(self, obj):
        return obj.jungle.champion.name_ko

    def mid_champion_name(self, obj):
        return obj.mid.champion.name_ko

    def adc_champion_name(self, obj):
        return obj.adc.champion.name_ko

    def support_champion_name(self, obj):
        return obj.support.champion.name_ko

    top_champion_name.short_description = "Top Champion"
    jungle_champion_name.short_description = "Jungle Champion"
    mid_champion_name.short_description = "Mid Champion"
    adc_champion_name.short_description = "ADC Champion"
    support_champion_name.short_description = "Support Champion"


class MatchForm(forms.ModelForm):
    """Custom form for the Match model."""

    class Meta:
        model = EsportsGame
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("form 사용됨")

        # MatchAdmin에서 이미 select_related로 최적화된 쿼리셋을 사용
        if "instance" in kwargs:
            instance = kwargs["instance"]
            if instance:
                # blue_composition과 red_composition의 관련된 챔피언을 미리 로드
                self.fields["blue_composition"].queryset = (
                    TeamComposition.objects.select_related(
                        "top__champion",
                        "jungle__champion",
                        "mid__champion",
                        "adc__champion",
                        "support__champion",
                    ).filter(top__champion__ban_count__lt=10)
                )

                self.fields["red_composition"].queryset = (
                    TeamComposition.objects.select_related(
                        "top__champion",
                        "jungle__champion",
                        "mid__champion",
                        "adc__champion",
                        "support__champion",
                    ).filter(top__champion__ban_count__lt=10)
                )

        # blue_team과 red_team에 대해서도 선택할 수 있는 팀을 제한
        self.fields["blue_team"].queryset = self.fields["blue_team"].queryset.filter(
            name__icontains="Team"
        )
        self.fields["red_team"].queryset = self.fields["red_team"].queryset.filter(
            name__icontains="Team"
        )


class MatchAdmin(admin.ModelAdmin):
    form = MatchForm

    list_display = (
        "date",
        "blue_team",
        "red_team",
        "winner",
        "get_blue_composition",
        "get_red_composition",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "blue_team",
            "red_team",
            "winner",
            "blue_composition",
            "red_composition",
        )

        return qs

    def get_blue_composition(self, obj):
        return str(obj.blue_composition)

    def get_red_composition(self, obj):
        return str(obj.red_composition)

    get_blue_composition.short_description = "Blue Composition"
    get_red_composition.short_description = "Red Composition"




@admin.register(LoLUser)
class LoLUserAdmin(admin.ModelAdmin):
    search_fields = ["name", "tag"]
    list_display = ("name", "tag", "tier", "division", "lp", "wins", "losses")
    list_filter = ("tier", "division")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.order_by("-lp")
        return qs


@admin.register(AdcSupportComposition)
class AdcSupportCompositionAdmin(admin.ModelAdmin):
    list_display = (
        "patch",
        "adc_champion_name",
        "support_champion_name",
        "pick_count",
        "win_count",
    )
    list_filter = ("patch", "adc", "support")
    autocomplete_fields = ["adc", "support"]
    search_fields = ["adc__champion__name_ko", "support__champion__name_ko"]

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .order_by("patch__version", "-pick_count", "-win_count")
        )
        qs = qs.select_related("adc__champion", "support__champion", "patch")
        return qs

    # 캐시된 select_related 필드 사용
    def adc_champion_name(self, obj):
        return obj.adc.champion.name_ko

    def support_champion_name(self, obj):
        return obj.support.champion.name_ko

    # Admin에서 보일 컬럼명 설정
    adc_champion_name.short_description = "ADC Champion"
    support_champion_name.short_description = "Support Champion"


@admin.register(TopJungleMidComposition)
class TopJungleMidCompositionAdmin(admin.ModelAdmin):
    list_display = (
        "patch",
        "top_champion_name",
        "jungle_champion_name",
        "mid_champion_name",
        "pick_count",
        "win_count",
    )
    list_filter = ("patch", "top", "jungle", "mid")

    # ForeignKey 필드를 자동 완성 필드로 지정
    autocomplete_fields = ["top", "jungle", "mid"]

    # PositionChampion 모델의 필드를 기반으로 검색
    search_fields = [
        "top__champion__name_ko",
        "jungle__champion__name_ko",
        "mid__champion__name_ko",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # ForeignKey와 연관된 모델들까지 한번에 로드
        return qs.select_related(
            "patch",
            "top",
            "top__champion",
            "jungle",
            "jungle__champion",
            "mid",
            "mid__champion",
        ).order_by("patch__version", "-pick_count", "-win_count")

    # 캐시된 select_related 필드 사용
    def top_champion_name(self, obj):
        return obj.top.champion.name_ko

    def jungle_champion_name(self, obj):
        return obj.jungle.champion.name_ko

    def mid_champion_name(self, obj):
        return obj.mid.champion.name_ko

    # Admin에서 보일 컬럼명 설정
    top_champion_name.short_description = "Top Champion"
    jungle_champion_name.short_description = "Jungle Champion"
    mid_champion_name.short_description = "Mid Champion"

admin.site.register(PatchVersion)
# admin.site.register(EsportsGame, MatchAdmin)
# admin.site.register(Team)