"""empty message

Revision ID: 97db0fcf0b56
Revises: 24735d4ba243
Create Date: 2021-01-24 11:11:17.375892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97db0fcf0b56'
down_revision = '24735d4ba243'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_catalogues', sa.Column('property_name', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_catalogues', 'property_name')
    # ### end Alembic commands ###
