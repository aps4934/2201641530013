from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Url(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String(2048), nullable=False)
    shortcode = Column(String(32), unique=True, nullable=False)
    expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    click_count = Column(Integer, default=0)
    click_logs = Column(Text, nullable=True)  # Store as JSON string

    def __repr__(self):
        return f"<Url(original_url='{self.original_url}', shortcode='{self.shortcode}', expiry='{self.expiry}')>"