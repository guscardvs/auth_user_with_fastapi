import pathlib

from utils.config import Config
from utils.providers.database import DatabaseConfig

config = Config()

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_DIR = ROOT.parent

database_config = DatabaseConfig.from_env(config)
