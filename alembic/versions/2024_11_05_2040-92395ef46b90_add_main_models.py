"""Add main models

Revision ID: 92395ef46b90
Revises: 9d91a8e708b7
Create Date: 2024-11-05 20:40:30.186370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92395ef46b90'
down_revision: Union[str, None] = '9d91a8e708b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('available_time_slots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('time_slots', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_photos_id'), 'photos', ['id'], unique=False)
    op.create_table('services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('is_price_from', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('appointments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.Column('total_price', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_appointments_user_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_id'), 'appointments', ['id'], unique=False)
    op.create_index(op.f('ix_appointments_user_id'), 'appointments', ['user_id'], unique=False)
    op.create_table('appointment_service_association',
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], name='fk_appointment_service_association_appointment_id'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='fk_appointment_service_association_service_id'),
    sa.PrimaryKeyConstraint('appointment_id', 'service_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointment_service_association')
    op.drop_index(op.f('ix_appointments_user_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_id'), table_name='appointments')
    op.drop_table('appointments')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_services_id'), table_name='services')
    op.drop_table('services')
    op.drop_index(op.f('ix_photos_id'), table_name='photos')
    op.drop_table('photos')
    op.drop_table('available_time_slots')
    # ### end Alembic commands ###
