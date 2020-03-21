"""empty message

Revision ID: 693514c17ec4
Revises: c933ea0b706e
Create Date: 2020-03-21 02:09:58.093573

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '693514c17ec4'
down_revision = 'c933ea0b706e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_ganres',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'genre_id')
    )
    op.create_table('venue_ganres',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'genre_id')
    )
    op.drop_column('Artist', 'genres')
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR(length=120)), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR(length=120)), autoincrement=False, nullable=True))
    op.drop_table('venue_ganres')
    op.drop_table('artist_ganres')
    op.drop_table('Genre')
    # ### end Alembic commands ###
