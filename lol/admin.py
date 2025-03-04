from django.contrib import admin

from lol.models import AdCarryChampion, Champion, Match, SupportChampion, Team, TeamComposition, TopChampion, JungleChampion, MidChampion

# Register your models here.
admin.site.register(Champion)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(TeamComposition)
admin.site.register(TopChampion)
admin.site.register(JungleChampion)
admin.site.register(MidChampion)
admin.site.register(AdCarryChampion)
admin.site.register(SupportChampion)
