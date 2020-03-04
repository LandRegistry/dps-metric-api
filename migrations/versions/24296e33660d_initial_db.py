"""Initial Database

Revision ID: 24296e33660d
Revises:
Create Date: 2019-07-02 13:26:38.236336

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app


# revision identifiers, used by Alembic.
revision = '24296e33660d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dps_user',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('ckan_user_id', sa.String(), nullable=False),
                    sa.Column('user_type', sa.String(), nullable=False),
                    sa.Column('status', sa.String(), nullable=False),
                    sa.Column('date_added', sa.DateTime(timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('user_id')
                    )
    op.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE dps_user TO " + current_app.config.get('APP_SQL_USERNAME'))
    op.execute("GRANT USAGE, SELECT ON dps_user_user_id_seq TO " + current_app.config.get('APP_SQL_USERNAME'))

    op.create_table('dps_activity',
                    sa.Column('activity_id', sa.Integer(), nullable=False),
                    sa.Column('activity_type', sa.String(), nullable=False),
                    sa.Column('dataset', sa.String(), nullable=True),
                    sa.Column('filename', sa.String(), nullable=True),
                    sa.Column('ckan_user_id', sa.String(), nullable=False),
                    sa.Column('date_added', sa.DateTime(timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('activity_id')
                    )
    op.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE dps_activity TO " + current_app.config.get('APP_SQL_USERNAME'))
    op.execute("GRANT USAGE, SELECT ON dps_activity_activity_id_seq TO " + current_app.config.get('APP_SQL_USERNAME'))


def downgrade():
    op.drop_table('dps_user')
    op.drop_table('dps_activity')
