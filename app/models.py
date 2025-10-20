from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class SMTPSettings(Base):
    __tablename__ = "smtp_settings"
    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, default="smtp.gmail.com")
    port = Column(Integer, default=587)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    use_tls = Column(Boolean, default=True)

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    full_name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    tax_id = Column(String, nullable=True)  # TC/Vergi No
    answers = Column(JSON, nullable=False)  # dynamic tree answers
    meta = Column(JSON, nullable=True)      # client meta (ua, ip, etc.)
    pdf_path = Column(String, nullable=True)
