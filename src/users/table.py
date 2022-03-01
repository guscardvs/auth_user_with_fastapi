import sqlalchemy as sa

from src.core.metadata import metadata
from utils.guid import GUID

user_table = sa.Table(
    'user',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('external_id', GUID(), index=True),
    sa.Column('name', sa.String(50)),
    sa.Column('email', sa.String(255), unique=True),
    sa.Column('password', sa.String(255)),
    sa.Column('birth_date', sa.Date),
    sa.Column('date_joined', sa.TIMESTAMP(timezone=True)),
)
