"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables
    # These will be created automatically by Alembic based on the models
    pass


def downgrade():
    # Drop all tables
    # These will be dropped automatically by Alembic based on the models
    pass
