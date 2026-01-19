"""
SQLAlchemy models dla wydatków
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Expense(Base):
    """Model wydatku"""
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)

    # Receipt info
    image_path = Column(String(500), nullable=False)
    image_hash = Column(String(64))  # MD5 dla deduplikacji

    # Parsed data
    shop_name = Column(String(200))
    purchase_date = Column(DateTime)
    total_amount = Column(Float, nullable=False)
    tax_number = Column(String(50))  # NIP

    # Items (JSON array)
    items = Column(JSON)  # [{"name": "...", "price": ..., "quantity": ...}]

    # OCR raw data (backup)
    ocr_raw_text = Column(String)

    # Metadata
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(String(100))  # User ID/name (future)

    # Categories
    category = Column(String(100))  # "Groceries", "Transport", etc.
    tags = Column(JSON)  # Additional tags

    # Notes
    notes = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return {
            'id': self.id,
            'shop_name': self.shop_name,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'total_amount': self.total_amount,
            'items': self.items,
            'category': self.category,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
        }
