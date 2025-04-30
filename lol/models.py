"""LOL champion and team composition models."""

from django.db import models


class PatchVersion(models.Model):
    version = models.CharField(max_length=20, unique=True, null=False, blank=False)
    release_date = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return self.version


class Champion(models.Model):
    """Champion model representing a League of Legends champion."""

    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )
    name_ko = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )
    full_image_url = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    icon_image_url = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

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

    champion = models.OneToOneField(
        Champion,
        on_delete=models.CASCADE,
        related_name="top_champion",
    )


class JungleChampion(PositionChampion):
    """Jungle position champion statistics."""

    champion = models.OneToOneField(
        Champion,
        on_delete=models.CASCADE,
        related_name="jungle_champion",
    )


class MidChampion(PositionChampion):
    """Mid lane champion statistics."""

    champion = models.OneToOneField(
        Champion,
        on_delete=models.CASCADE,
        related_name="mid_champion",
    )


class AdCarryChampion(PositionChampion):
    """AD Carry champion statistics."""

    champion = models.OneToOneField(
        Champion,
        on_delete=models.CASCADE,
        related_name='adc_champion'
    )


class SupportChampion(PositionChampion):
    """Support champion statistics."""

    champion = models.OneToOneField(
        Champion,
        on_delete=models.CASCADE,
        related_name="support_champion",
    )


class Team(models.Model):
    """Team model representing a League of Legends team."""

    name = models.CharField(max_length=100, unique=True)
    image_url = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Match(models.Model):
    """Match history for reference."""
    date = models.DateField()
    sets = models.IntegerField(default=0)
    patch = models.CharField(max_length=10)
    blue_composition = models.ForeignKey(
        to='TeamComposition',
        on_delete=models.DO_NOTHING,
        related_name="blue_team_matches",
        null=True
    )
    red_composition = models.ForeignKey(
        to='TeamComposition',
        on_delete=models.DO_NOTHING,
        related_name="red_team_matches",
        null=True
    )
    blue_team = models.ForeignKey(
        to='Team',
        on_delete=models.DO_NOTHING,
        related_name="blue_team_matches"
    )
    red_team = models.ForeignKey(
        to='Team',
        on_delete=models.DO_NOTHING,
        related_name="red_team_matches"
    )
    winner = models.ForeignKey(
        to='Team',
        on_delete=models.DO_NOTHING,
        related_name="winner_matches"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.blue_team} vs {self.red_team}"


# TODO created_at, update_at
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
