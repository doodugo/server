from django import forms
from django.contrib import admin

from lol.models import AdCarryChampion, Champion, Match, SupportChampion, Team, TeamComposition, TopChampion, JungleChampion, MidChampion

# Register your models here.
admin.site.register(Champion)
admin.site.register(Team)
admin.site.register(TeamComposition)
admin.site.register(TopChampion)
admin.site.register(JungleChampion)
admin.site.register(MidChampion)
admin.site.register(AdCarryChampion)
admin.site.register(SupportChampion)


class MatchForm(forms.ModelForm):
    """Custom form for the Match model."""
    
    class Meta:
        model = Match
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


admin.site.register(Match, MatchAdmin)
