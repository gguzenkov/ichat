from sqlalchemy import Column, DateTime
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    op.add_column('users', Column('last_active', DateTime, default=datetime.utcnow))

def downgrade():
    op.drop_column('users', 'last_active') 