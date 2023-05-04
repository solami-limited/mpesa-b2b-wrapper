import enum
from sqlalchemy.sql import func
from src import db


class StatusEnum(enum.Enum):
    """Status Enum"""
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class B2B(db.Model):
    """B2B Model"""
    __tablename__ = 'mpesa_b2b_transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    pnr = db.Column(db.String(100), unique=True, index=True, nullable=False)
    originator_conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    conversation_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.PENDING)
    created_on = db.Column(db.DateTime, index=True, server_default=func.now(), nullable=False)
    updated_on = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
