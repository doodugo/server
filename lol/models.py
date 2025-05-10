"""LOL champion and team composition models."""

from django.db import models
from django.db.models import Q


class LoLUser(models.Model):
    puuid = models.CharField(max_length=100, unique=True, null=False, blank=False)
    name = models.CharField(max_length=64, null=True, blank=True)
    tag = models.CharField(max_length=32, null=True, blank=True)
    tier = models.CharField(max_length=10, null=False, blank=False)
    division = models.CharField(max_length=10, null=False, blank=False)
    lp = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}#{self.tag}"


class PatchVersion(models.Model):
    version = models.CharField(max_length=20, unique=True, null=False, blank=False)
    release_date = models.DateTimeField(null=False, blank=False)
    last_crawl_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.version


class Champion(models.Model):
    """Champion model representing a League of Legends champion."""

    id = models.IntegerField(unique=True, null=False, blank=False, primary_key=True)
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
    full_image_url = models.CharField(max_length=200, blank=True, null=True)
    icon_image_url = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Position(models.TextChoices):
    TOP = "TOP", "Top"
    JUNGLE = "JUNGLE", "Jungle"
    MID = "MID", "Mid"
    ADC = "ADC", "Adc"
    SUPPORT = "SUPPORT", "Support"


class PositionChampion(models.Model):
    champion = models.ForeignKey(
        Champion,
        on_delete=models.CASCADE,
    )
    patch = models.ForeignKey(
        PatchVersion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    position = models.CharField(max_length=20, choices=Position.choices)
    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.champion.name)

    @property
    def win_rate(self):
        """Calculate win rate percentage."""
        if self.pick_count == 0:
            return 0
        return (self.win_count / self.pick_count) * 100

    class Meta:
        unique_together = ["patch", "champion", "position"]


class CounterRecord(models.Model):
    patch = models.ForeignKey(
        "PatchVersion", on_delete=models.CASCADE, null=True, blank=True
    )
    position = models.CharField(max_length=20, choices=Position.choices)
    champion_a = models.ForeignKey(
        Champion, on_delete=models.CASCADE, related_name="counter_a"
    )
    champion_b = models.ForeignKey(
        Champion, on_delete=models.CASCADE, related_name="counter_b"
    )
    wins_a = models.IntegerField(default=0)
    wins_b = models.IntegerField(default=0)

    class Meta:
        unique_together = [("patch", "position", "champion_a", "champion_b")]

    def __str__(self):
        return f"{self.champion_a.name} vs {self.champion_b.name} ({self.position})"

    @property
    def total_matches(self):
        return self.wins_a + self.wins_b

    @property
    def win_rate_a(self):
        if self.total_matches == 0:
            return 0
        return (self.wins_a / self.total_matches) * 100

    @property
    def win_rate_b(self):
        if self.total_matches == 0:
            return 0
        return (self.wins_b / self.total_matches) * 100

    @staticmethod
    def get_or_create_record(patch, position, champ1, champ2):
        """
        Check if the record already exists, if so update it; otherwise, create a new record.
        """
        champion_a, champion_b = min(champ1, champ2, key=lambda c: c.id), max(
            champ1, champ2, key=lambda c: c.id
        )

        record, created = CounterRecord.objects.get_or_create(
            patch=patch, position=position, champion_a=champion_a, champion_b=champion_b
        )

        return record, created

    @staticmethod
    def find_record(patch, position, champ1, champ2):
        """
        Retrieve the record by checking both combinations: (champion_a, champion_b) and (champion_b, champion_a)
        """
        return CounterRecord.objects.filter(
            Q(patch=patch)
            & Q(position=position)
            & (
                (Q(champion_a=champ1) & Q(champion_b=champ2))
                | (Q(champion_a=champ2) & Q(champion_b=champ1))
            )
        ).first()


class Team(models.Model):
    """Team model representing a League of Legends team."""

    name = models.CharField(max_length=100, unique=True)
    image_url = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class EsportsGame(models.Model):
    date = models.DateField()
    sets = models.IntegerField(default=0)
    patch = models.CharField(max_length=10)
    blue_composition = models.ForeignKey(
        "TeamComposition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="blue_compositions",
    )
    red_composition = models.ForeignKey(
        "TeamComposition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="red_compositions",
    )
    blue_team = models.ForeignKey(
        "Team",
        on_delete=models.DO_NOTHING,
        related_name="blue_team_games",
    )
    red_team = models.ForeignKey(
        "Team",
        on_delete=models.DO_NOTHING,
        related_name="red_team_games",
    )
    winner = models.ForeignKey(
        "Team",
        on_delete=models.DO_NOTHING,
        related_name="won_games",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.blue_team} vs {self.red_team}"


class TeamComposition(models.Model):
    patch = models.ForeignKey(
        "PatchVersion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    top = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.TOP},
        related_name="top_team_compositions",
    )
    jungle = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.JUNGLE},
        related_name="jungle_team_compositions",
    )
    mid = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.MID},
        related_name="mid_team_compositions",
    )
    adc = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.ADC},
        related_name="adc_team_compositions",
    )
    support = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.SUPPORT},
        related_name="support_team_compositions",
    )
    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Team Comp (Patch: {self.patch})"

    @property
    def win_rate(self):
        if self.pick_count == 0:
            return 0
        return (self.win_count / self.pick_count) * 100


class Match(models.Model):
    match_id = models.BigIntegerField(unique=True, null=False, blank=False)
    region = models.CharField(max_length=20, null=False, blank=False)
    blue_team = models.ForeignKey(
        TeamComposition, on_delete=models.CASCADE, related_name="blue_team_matches"
    )
    red_team = models.ForeignKey(
        TeamComposition, on_delete=models.CASCADE, related_name="red_team_matches"
    )


class TopJungleMidComposition(models.Model):
    patch = models.ForeignKey(
        PatchVersion,
        on_delete=models.CASCADE,
    )
    top = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.TOP},
        related_name="top_compositions",
    )
    jungle = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.JUNGLE},
        related_name="jungle_compositions",
    )
    mid = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.MID},
        related_name="mid_compositions",
    )

    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ["patch", "top", "jungle", "mid"]

    def __str__(self):
        return f"({self.top.champion.name}, {self.jungle.champion.name}, {self.mid.champion.name})"


class AdcSupportComposition(models.Model):
    patch = models.ForeignKey(
        PatchVersion,
        on_delete=models.CASCADE,
    )
    adc = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.ADC},
        related_name="adc_compositions",
    )
    support = models.ForeignKey(
        PositionChampion,
        on_delete=models.CASCADE,
        limit_choices_to={"position": Position.SUPPORT},
        related_name="support_compositions",
    )

    pick_count = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ["patch", "adc", "support"]

    def __str__(self):
        return f"({self.adc.champion.name}, {self.support.champion.name})"
