from datetime import datetime
from zoneinfo import ZoneInfo

AMERICA_SAO_PAULO = 'America/Sao_Paulo'


def now(zone: str = AMERICA_SAO_PAULO):
    return datetime.now(tz=ZoneInfo(zone))


def today(zone: str = AMERICA_SAO_PAULO):
    return now(zone).date()
