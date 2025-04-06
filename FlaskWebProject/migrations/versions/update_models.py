"""update models with new fields

Revision ID: 2a1b3c4d5e6f
Revises: initial_migration
Create Date: 2024-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a1b3c4d5e6f'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Add room_status to Room table
    op.add_column('room', sa.Column('room_status', sa.String(length=20), nullable=True))
    op.execute("UPDATE room SET room_status = 'available' WHERE room_status IS NULL")
    
    # Add check_in_time and check_out_time to Booking table
    op.add_column('booking', sa.Column('check_in_time', sa.DateTime(), nullable=True))
    op.add_column('booking', sa.Column('check_out_time', sa.DateTime(), nullable=True))
    
    # Create Invoice table
    op.create_table('invoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('issue_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('tax', sa.Float(), nullable=False),
        sa.Column('is_paid', sa.Boolean(), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('invoice')
    op.drop_column('booking', 'check_out_time')
    op.drop_column('booking', 'check_in_time')
    op.drop_column('room', 'room_status')
