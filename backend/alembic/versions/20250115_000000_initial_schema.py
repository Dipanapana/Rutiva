"""Initial RUTA database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'parent', 'school_admin', 'super_admin')")
    op.execute("CREATE TYPE orderstatus AS ENUM ('pending', 'paid', 'failed', 'refunded', 'cancelled')")
    op.execute("CREATE TYPE paymentprovider AS ENUM ('payfast', 'yoco', 'eft', 'school_license')")
    op.execute("CREATE TYPE tutorplan AS ENUM ('starter', 'standard', 'unlimited')")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', postgresql.ENUM('student', 'parent', 'school_admin', 'super_admin', name='userrole', create_type=False), nullable=False, server_default='student'),
        sa.Column('grade', sa.Integer, nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('province', sa.String(50), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # OTP Codes table
    op.create_table(
        'otp_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('purpose', sa.String(20), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_otp_codes_user_purpose', 'otp_codes', ['user_id', 'purpose'])

    # Parent-Child relationships
    op.create_table(
        'parent_child',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('parent_id', 'child_id', name='uq_parent_child'),
    )

    # Subjects table
    op.create_table(
        'subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # Products table (Study Guides)
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sku', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('subjects.id'), nullable=False),
        sa.Column('grade', sa.Integer, nullable=False),
        sa.Column('term', sa.Integer, nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('price_zar', sa.Integer, nullable=False),
        sa.Column('sale_price_zar', sa.Integer, nullable=True),
        sa.Column('content_json', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('total_pages', sa.Integer, nullable=True),
        sa.Column('total_hours', sa.Integer, nullable=True),
        sa.Column('is_published', sa.Boolean, server_default='false'),
        sa.Column('is_featured', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )
    op.create_index('ix_products_grade_term', 'products', ['grade', 'term'])

    # Bundles table
    op.create_table(
        'bundles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sku', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('price_zar', sa.Integer, nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('is_published', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Bundle-Products association table
    op.create_table(
        'bundle_products',
        sa.Column('bundle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bundles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    )

    # Promo Codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('discount_percent', sa.Integer, nullable=True),
        sa.Column('discount_amount_zar', sa.Integer, nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_uses', sa.Integer, nullable=True),
        sa.Column('current_uses', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # Orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_number', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('status', postgresql.ENUM('pending', 'paid', 'failed', 'refunded', 'cancelled', name='orderstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('subtotal_zar', sa.Integer, nullable=False),
        sa.Column('discount_zar', sa.Integer, server_default='0'),
        sa.Column('total_zar', sa.Integer, nullable=False),
        sa.Column('payment_provider', postgresql.ENUM('payfast', 'yoco', 'eft', 'school_license', name='paymentprovider', create_type=False), nullable=True),
        sa.Column('payment_reference', sa.String(100), nullable=True),
        sa.Column('promo_code_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('promo_codes.id'), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Order Items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('bundle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bundles.id'), nullable=True),
        sa.Column('price_zar', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # User Library table (purchased products)
    op.create_table(
        'user_library',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=True),
        sa.Column('download_count', sa.Integer, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress_percent', sa.Integer, server_default='0'),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('user_id', 'product_id', name='uq_user_library'),
    )
    op.create_index('ix_user_library_user_id', 'user_library', ['user_id'])

    # Timetables table
    op.create_table(
        'timetables',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('exam_date', sa.Date, nullable=False),
        sa.Column('settings', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('schedule', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )
    op.create_index('ix_timetables_user_id', 'timetables', ['user_id'])

    # Timetable Progress table
    op.create_table(
        'timetable_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('timetable_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('timetables.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_date', sa.Date, nullable=False),
        sa.Column('session_index', sa.Integer, nullable=False),
        sa.Column('completed', sa.Boolean, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.UniqueConstraint('timetable_id', 'session_date', 'session_index', name='uq_timetable_progress'),
    )

    # Tutor Subscriptions table
    op.create_table(
        'tutor_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plan', postgresql.ENUM('starter', 'standard', 'unlimited', name='tutorplan', create_type=False), nullable=False),
        sa.Column('questions_limit', sa.Integer, nullable=True),
        sa.Column('questions_used', sa.Integer, server_default='0'),
        sa.Column('price_zar', sa.Integer, nullable=False),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_tutor_subscriptions_user_id', 'tutor_subscriptions', ['user_id'])

    # Chat Sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('topic', sa.String(255), nullable=True),
        sa.Column('question_count', sa.Integer, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    # Chat Messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])

    # Schools table
    op.create_table(
        'schools',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('emis_number', sa.String(20), unique=True, nullable=True),
        sa.Column('province', sa.String(50), nullable=False),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # School Admins table
    op.create_table(
        'school_admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_primary', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('school_id', 'user_id', name='uq_school_admin'),
    )

    # School Orders table
    op.create_table(
        'school_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('learner_count', sa.Integer, nullable=False),
        sa.Column('price_per_learner_zar', sa.Integer, nullable=False),
        sa.Column('total_zar', sa.Integer, nullable=False),
        sa.Column('payment_status', sa.String(20), server_default='pending'),
        sa.Column('payment_reference', sa.String(100), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # School Licenses table
    op.create_table(
        'school_licenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('school_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('school_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('school_order_id', 'user_id', name='uq_school_license'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('school_licenses')
    op.drop_table('school_orders')
    op.drop_table('school_admins')
    op.drop_table('schools')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('tutor_subscriptions')
    op.drop_table('timetable_progress')
    op.drop_table('timetables')
    op.drop_table('user_library')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('promo_codes')
    op.drop_table('bundle_products')
    op.drop_table('bundles')
    op.drop_table('products')
    op.drop_table('subjects')
    op.drop_table('parent_child')
    op.drop_table('otp_codes')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE tutorplan')
    op.execute('DROP TYPE paymentprovider')
    op.execute('DROP TYPE orderstatus')
    op.execute('DROP TYPE userrole')
