from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # TENAGA_KESEHATAN, ADMIN
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    checkups = relationship("Checkup", back_populates="checked_by")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    medical_record_number = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, index=True)
    date_of_birth = Column(String) # Storing as string YYYY-MM-DD for simplicity
    gender = Column(String) # M/F
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    checkups = relationship("Checkup", back_populates="patient")

class Checkup(Base):
    __tablename__ = "checkups"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    checked_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Input Data
    age_years = Column(Integer)
    gender = Column(Integer) # 1 or 2 as per model
    bmi = Column(Float)
    map = Column(Float)
    cholesterol = Column(Integer)
    gluc = Column(Integer)
    smoke = Column(Integer)
    alco = Column(Integer)
    active = Column(Integer)

    # Output Data
    probability = Column(Float)
    risk_label = Column(Integer)
    risk_category = Column(String)
    model_version = Column(String)

    notes = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    shap_values = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="checkups")
    checked_by = relationship("User", back_populates="checkups")
