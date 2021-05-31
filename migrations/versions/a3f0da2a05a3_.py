"""empty message

Revision ID: a3f0da2a05a3
Revises: 97db0fcf0b56
Create Date: 2021-01-24 11:54:03.070790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f0da2a05a3'
down_revision = '97db0fcf0b56'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_catalogues', sa.Column('id_ru', sa.Integer(), nullable=True))
    op.add_column('user_catalogues', sa.Column('link', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_catalogues', 'link')
    op.drop_column('user_catalogues', 'id_ru')
    # ### end Alembic commands ###