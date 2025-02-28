from django.db import models

# Create your models here.
class Champion(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )
    image_url = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.name

class PositionChampion(models.Model):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        unique=True
    )
    pick_count = models.IntegerField(
        default=0,
    )
    win_count = models.IntegerField(
        default=0,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.champion.name}"

    @property
    def win_rate(self):
        if self.pick_count == 0:
            return 0
        return (self.win_count / self.pick_count) * 100

class TopChampion(PositionChampion):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="top_champion",
        unique=True
    )

class JungleChampion(PositionChampion):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="jungle_champion",
        unique=True
    )

class MidChampion(PositionChampion):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="mid_champion",
        unique=True
    )


class AdCarryChampion(models.Model):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="ad_carry_champion",
        unique=True
    )


class SupportChampion(PositionChampion):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="bot_champion",
        unique=True
    )
