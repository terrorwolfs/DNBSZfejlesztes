"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-03-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from enum import Enum

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

class UserRole(Enum):
    GUEST = 'GUEST'
    RECEPTIONIST = 'RECEPTIONIST'
    ADMIN = 'ADMIN'

def upgrade():
    # Create enum type for user roles
    sa.Enum('GUEST', 'RECEPTIONIST', 'ADMIN', name='userrole').create(op.get_bind())
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=60), nullable=False),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('address', sa.String(length=200)),
        sa.Column('role', sa.Enum(UserRole), default=UserRole.GUEST, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    op.create_table('room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.Integer(), nullable=False),
        sa.Column('room_type', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('price_per_night', sa.Float(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('amenities', sa.JSON()),
        sa.Column('status', sa.String(length=20), default='available'),
        sa.Column('floor', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('booking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), default='pending'),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('check_in_time', sa.DateTime()),
        sa.Column('check_out_time', sa.DateTime()),
        sa.Column('special_requests', sa.Text()),
        sa.ForeignKeyConstraint(['guest_id'], ['user.id']),
        sa.ForeignKeyConstraint(['room_id'], ['room.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('extra_service',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('booking.id'), nullable=False),
        sa.Column('service_date', sa.DateTime(), default=datetime.utcnow),
        sa.Column('status', sa.String(length=20), default='pending'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('room.id'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('status', sa.String(length=20), default='scheduled'),
        sa.Column('maintenance_type', sa.String(length=50)),
        sa.Column('technician', sa.String(length=100)),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('invoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('booking.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), default='pending'),
        sa.Column('issue_date', sa.DateTime(), default=datetime.utcnow),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('payment_date', sa.DateTime()),
        sa.Column('payment_method', sa.String(length=50)),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('invoice')
    op.drop_table('maintenance')
    op.drop_table('extra_service')
    op.drop_table('booking')
    op.drop_table('room')
    op.drop_table('user')
    sa.Enum(name='userrole').drop(op.get_bind())
