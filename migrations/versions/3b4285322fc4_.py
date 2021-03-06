"""empty message

Revision ID: 3b4285322fc4
Revises: f93a8bcf7939
Create Date: 2020-10-02 17:26:58.223318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b4285322fc4'
down_revision = 'f93a8bcf7939'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('generes')
    # ### end Alembic commands ###
