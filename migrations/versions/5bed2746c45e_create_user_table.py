"""create user table

Revision ID: 5bed2746c45e
Revises: 
Create Date: 2022-02-28 16:32:56.009451

"""
from alembic import op
import sqlalchemy as sa
import utils.guid

# revision identifiers, used by Alembic.
revision = '5bed2746c45e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('external_id', utils.guid.GUID(length=32), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('date_joined', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_external_id'), 'user', ['external_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_external_id'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###