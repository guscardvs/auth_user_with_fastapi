import sqlalchemy as sa

from src.core import settings
from src.core.metadata import metadata
from utils.finder import InstanceFinder


def get_metadata():
    finder = InstanceFinder(sa.Table, settings.ROOT)
    finder.find()
    return metadata
