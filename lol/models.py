"""LOL champion and team composition models."""
from django.db import models


class Champion(models.Model):
    """Champion model representing a League of Legends champion."""

    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )
    image_url = models.CharField(max_length=200)
    ban_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class PositionChampion(models.Model):
    """Abstract base model for position-specific champion stats."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        unique=True,
    )
    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.champion.name)

    @property
    def win_rate(self):
        """Calculate win rate percentage."""
        if self.pick_count == 0:
            return 0
        return (self.win_count / self.pick_count) * 100


class TopChampion(PositionChampion):
    """Top lane champion statistics."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="top_champion",
        unique=True,
    )


class JungleChampion(PositionChampion):
    """Jungle position champion statistics."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="jungle_champion",
        unique=True,
    )


class MidChampion(PositionChampion):
    """Mid lane champion statistics."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="mid_champion",
        unique=True,
    )


class AdCarryChampion(PositionChampion):
    """AD Carry champion statistics."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="ad_carry_champion",
        unique=True,
    )


class SupportChampion(PositionChampion):
    """Support champion statistics."""

    champion = models.ForeignKey(
        Champion,
        on_delete=models.DO_NOTHING,
        related_name="support_champion",
        unique=True,
    )


class Match(models.Model):
    """Match history for reference."""
    date = models.DateField()
    patch = models.CharField(max_length=10)
    blue_team = models.CharField(max_length=100)
    red_team = models.CharField(max_length=100)
    winner = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.blue_team} vs {self.red_team}"


class MatchComposition(models.Model):
    """Link between Match and TeamComposition."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    composition = models.ForeignKey('TeamComposition', on_delete=models.CASCADE)
    is_blue_side = models.BooleanField()
    is_winner = models.BooleanField()

    class Meta:
        unique_together = ['match', 'is_blue_side']


class TeamComposition(models.Model):
    """Team composition model focusing on champion combinations."""
    top = models.ForeignKey(
        TopChampion,
        on_delete=models.CASCADE,
        related_name='team_compositions',
    )
    jungle = models.ForeignKey(
        JungleChampion,
        on_delete=models.CASCADE,
        related_name='team_compositions',
    )
    mid = models.ForeignKey(
        MidChampion,
        on_delete=models.CASCADE,
        related_name='team_compositions',
    )
    adc = models.ForeignKey(
        AdCarryChampion,
        on_delete=models.CASCADE,
        related_name='team_compositions',
    )
    support = models.ForeignKey(
        SupportChampion,
        on_delete=models.CASCADE,
        related_name='team_compositions',
    )
    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['top', 'jungle', 'mid', 'adc', 'support']

    def __str__(self):
        return (
            f"({self.top.champion.name}, {self.jungle.champion.name}, "
            f"{self.mid.champion.name}, {self.adc.champion.name}, "
            f"{self.support.champion.name})"
        )

    @property
    def win_rate(self):
        if self.pick_count == 0:
            return 0
        return (self.win_count / self.pick_count) * 100
