"""add public_id to invoice

Revision ID: 3a2b4c5d6e7f
Revises: 2a1b3c4d5e6f
Create Date: 2024-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '3a2b4c5d6e7f'
down_revision = '2a1b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade():
    # Add public_id column to Invoice table
    op.add_column('invoice', sa.Column('public_id', sa.String(length=36), nullable=True))
    
    # Generate UUID for existing invoices
    from sqlalchemy.sql import table, column
    from sqlalchemy import String
    invoice_table = table('invoice', column('id', sa.Integer), column('public_id', String(36)))
    
    connection = op.get_bind()
    for invoice in connection.execute(sa.select([invoice_table.c.id])).fetchall():
        connection.execute(
            invoice_table.update().
            where(invoice_table.c.id == invoice[0]).
            values(public_id=str(uuid.uuid4()))
        )
    
    # Make public_id not nullable and unique
    op.alter_column('invoice', 'public_id', nullable=False)
    op.create_unique_constraint('uq_invoice_public_id', 'invoice', ['public_id'])


def downgrade():
    op.drop_constraint('uq_invoice_public_id', 'invoice', type_='unique')
    op.drop_column('invoice', 'public_id')
