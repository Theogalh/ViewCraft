"""Adding new columns in models guilds, roster, and character

Revision ID: 3188f5f0b39a
Revises: b8b8d677ec95
Create Date: 2019-04-01 15:08:26.499154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3188f5f0b39a'
down_revision = 'b8b8d677ec95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('character', sa.Column('armory_link', sa.String(length=280), nullable=True))
    op.add_column('character', sa.Column('classe', sa.String(length=24), nullable=True))
    op.add_column('character', sa.Column('ilevel', sa.Float(), nullable=True))
    op.add_column('character', sa.Column('level', sa.Integer(), nullable=True))
    op.add_column('character', sa.Column('race', sa.String(length=24), nullable=True))
    op.add_column('character', sa.Column('rio_link', sa.String(length=280), nullable=True))
    op.add_column('character', sa.Column('rio_score', sa.Integer(), nullable=True))
    op.add_column('character', sa.Column('wlog_link', sa.String(length=280), nullable=True))
    op.add_column('guild', sa.Column('armory_link', sa.String(length=280), nullable=True))
    op.add_column('guild', sa.Column('wowprogress_link', sa.String(length=280), nullable=True))
    op.add_column('roster', sa.Column('ilvl_average', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roster', 'ilvl_average')
    op.drop_column('guild', 'wowprogress_link')
    op.drop_column('guild', 'armory_link')
    op.drop_column('character', 'wlog_link')
    op.drop_column('character', 'rio_score')
    op.drop_column('character', 'rio_link')
    op.drop_column('character', 'race')
    op.drop_column('character', 'level')
    op.drop_column('character', 'ilevel')
    op.drop_column('character', 'classe')
    op.drop_column('character', 'armory_link')
    # ### end Alembic commands ###
