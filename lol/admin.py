from django import forms
from django.contrib import admin

from lol.models import AdcSupportComposition, Champion, EsportsGame, LoLUser, Match, PatchVersion, PositionChampion, Team, TeamComposition, TopJungleMidComposition
from django.utils.translation import gettext_lazy as _
# Register your models here.
admin.site.register(Champion)
admin.site.register(Team)


class ChampionFilter(admin.SimpleListFilter):
    """Base class for champion filters in different positions"""
    title = _('Champion')  # Default title, will be overridden by subclasses
    parameter_name = 'champion'  # Default parameter name, will be overridden by subclasses
    position_field = None  # Will be set by subclasses
    
    def lookups(self, request, model_admin):
        # Get distinct champions for this position
        position_field = self.position_field
        champion_field = f"{position_field}__champion"
        
        # Get all unique champions in this position from the filtered queryset
        champions = model_admin.get_queryset(request).values_list(
            f"{champion_field}__name", 
            f"{champion_field}__name_ko"
        ).distinct().order_by(f"{champion_field}__name")
        
        # Return as (value, display_name) tuples
        return [(name, f"{name_ko} ({name})" if name_ko else name) for name, name_ko in champions]
    
    def queryset(self, request, queryset):
        if self.value():
            # Filter the queryset when a value is selected
            filter_param = {f"{self.position_field}__champion__name": self.value()}
            return queryset.filter(**filter_param)
        return queryset


class TopChampionFilter(ChampionFilter):
    """Filter for champions in top position"""
    title = _('Top Champion')
    parameter_name = 'top_champion'
    position_field = 'top'


class JungleChampionFilter(ChampionFilter):
    """Filter for champions in jungle position"""
    title = _('Jungle Champion')
    parameter_name = 'jungle_champion'
    position_field = 'jungle'


class MidChampionFilter(ChampionFilter):
    """Filter for champions in mid position"""
    title = _('Mid Champion')
    parameter_name = 'mid_champion'
    position_field = 'mid'


class AdcChampionFilter(ChampionFilter):
    """Filter for champions in ADC position"""
    title = _('ADC Champion')
    parameter_name = 'adc_champion'
    position_field = 'adc'


class SupportChampionFilter(ChampionFilter):
    """Filter for champions in support position"""
    title = _('Support Champion')
    parameter_name = 'support_champion'
    position_field = 'support'


admin.site.register(PositionChampion)
admin.site.register(Match)
@admin.register(TeamComposition)
class TeamCompositionAdmin(admin.ModelAdmin):
    list_display = ('get_top_name', 'get_jungle_name', 'get_mid_name', 'get_adc_name', 'get_support_name', 'pick_count', 'win_count')
    list_filter = (
        TopChampionFilter,
        JungleChampionFilter,
        MidChampionFilter,
        AdcChampionFilter,
        SupportChampionFilter,
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "top__champion", "jungle__champion", "mid__champion", "adc__champion", "support__champion",
        ).order_by('top__champion__name')
        return qs
    
    # Custom display methods for list_display to avoid N+1 queries
    def get_top_name(self, obj):
        return obj.top.champion.name_ko if obj.top and obj.top.champion else "-"
    get_top_name.short_description = 'Top'
    get_top_name.admin_order_field = 'top__champion__name'
    
    def get_jungle_name(self, obj):
        return obj.jungle.champion.name_ko if obj.jungle and obj.jungle.champion else "-"
    get_jungle_name.short_description = 'Jungle'
    get_jungle_name.admin_order_field = 'jungle__champion__name'
    
    def get_mid_name(self, obj):
        return obj.mid.champion.name_ko if obj.mid and obj.mid.champion else "-"
    get_mid_name.short_description = 'Mid'
    get_mid_name.admin_order_field = 'mid__champion__name'
    
    def get_adc_name(self, obj):
        return obj.adc.champion.name_ko if obj.adc and obj.adc.champion else "-"
    get_adc_name.short_description = 'ADC'
    get_adc_name.admin_order_field = 'adc__champion__name'
    
    def get_support_name(self, obj):
        return obj.support.champion.name_ko if obj.support and obj.support.champion else "-"
    get_support_name.short_description = 'Support'
    get_support_name.admin_order_field = 'support__champion__name'


class MatchForm(forms.ModelForm):
    """Custom form for the Match model."""
    
    class Meta:
        model = EsportsGame
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('form 사용됨')

        # MatchAdmin에서 이미 select_related로 최적화된 쿼리셋을 사용
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance:
                # blue_composition과 red_composition의 관련된 챔피언을 미리 로드
                self.fields['blue_composition'].queryset = TeamComposition.objects.select_related(
                    'top__champion', 'jungle__champion', 'mid__champion', 'adc__champion', 'support__champion'
                ).filter(top__champion__ban_count__lt=10)

                self.fields['red_composition'].queryset = TeamComposition.objects.select_related(
                    'top__champion', 'jungle__champion', 'mid__champion', 'adc__champion', 'support__champion'
                ).filter(top__champion__ban_count__lt=10)

        # blue_team과 red_team에 대해서도 선택할 수 있는 팀을 제한
        self.fields['blue_team'].queryset = self.fields['blue_team'].queryset.filter(name__icontains="Team")
        self.fields['red_team'].queryset = self.fields['red_team'].queryset.filter(name__icontains="Team")


class MatchAdmin(admin.ModelAdmin):
    form = MatchForm

    list_display = ("date", "blue_team", "red_team", "winner", "get_blue_composition", "get_red_composition")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "blue_team", "red_team", "winner",  # Team 모델
            "blue_composition__top", "blue_composition__jungle", "blue_composition__mid", "blue_composition__adc", "blue_composition__support",  # blue composition
            "red_composition__top", "red_composition__jungle", "red_composition__mid", "red_composition__adc", "red_composition__support",  # red composition
            "blue_composition__top__champion", "blue_composition__jungle__champion", "blue_composition__mid__champion", "blue_composition__adc__champion", "blue_composition__support__champion",
            "red_composition__top__champion", "red_composition__jungle__champion", "red_composition__mid__champion", "red_composition__adc__champion", "red_composition__support__champion"
        )

        return qs

    def get_blue_composition(self, obj):
        return str(obj.blue_composition)

    def get_red_composition(self, obj):
        return str(obj.red_composition)

    get_blue_composition.short_description = "Blue Composition"
    get_red_composition.short_description = "Red Composition"


admin.site.register(EsportsGame, MatchAdmin)
admin.site.register(PatchVersion)
admin.site.register(LoLUser)

@admin.register(AdcSupportComposition)
class AdcSupportCompositionAdmin(admin.ModelAdmin):
    list_display = ('patch', 'adc', 'support', 'pick_count', 'win_count')
    list_filter = ('patch', 'adc', 'support')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('adc__champion', 'support__champion', 'patch')
        return qs

@admin.register(TopJungleMidComposition)
class TopJungleMidCompositionAdmin(admin.ModelAdmin):
    list_display = ('patch', 'top_name', 'jungle_name', 'mid_name', 'pick_count', 'win_count')
    list_filter = ('patch', 'top', 'jungle', 'mid')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 챔피언 정보도 함께 미리 로드
        return qs.select_related(
            'patch',
            'top', 
            'top__champion',
            'jungle', 
            'jungle__champion',
            'mid', 
            'mid__champion'
        )

    # 각 챔피언 이름을 직접 반환
    def top_name(self, obj):
        return obj.top.champion.name if obj.top and obj.top.champion else "Unknown Top"
    top_name.short_description = "Top Champion"

    def jungle_name(self, obj):
        return obj.jungle.champion.name if obj.jungle and obj.jungle.champion else "Unknown Jungle"
    jungle_name.short_description = "Jungle Champion"

    def mid_name(self, obj):
        return obj.mid.champion.name if obj.mid and obj.mid.champion else "Unknown Mid"
    mid_name.short_description = "Mid Champion"