from venv import logger
from django.db import transaction
from lol.models import LoLUser


class UserService:

    def save_user(
        self,
        puuid: str,
        name: str = None,
        tag: str = None,
        tier: str = None,
        division: str = None,
        lp: int = None,
        wins: int = None,
        losses: int = None,
    ) -> LoLUser:
        try:
            with transaction.atomic():
                user = LoLUser.objects.create_or_update(
                    puuid=puuid,
                    name=name,
                    tag=tag,
                    tier=tier,
                    division=division,
                    lp=lp,
                    wins=wins,
                    losses=losses,
                )
                return user
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            raise e
