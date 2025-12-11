from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- User ---
class UserBase(BaseModel):
    name: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Patient ---
class PatientBase(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str
    medical_record_number: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = True

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Checkup ---
class CheckupBase(BaseModel):
    age_years: int
    gender: int
    bmi: float
    map: float
    cholesterol: int
    gluc: int
    smoke: int
    alco: int
    active: int
    notes: Optional[str] = None

class CheckupCreate(CheckupBase):
    checked_by_user_id: int # In real app, this comes from token

class Checkup(CheckupBase):
    id: int
    patient_id: int
    checked_by_user_id: int
    probability: float
    risk_label: int
    risk_category: str
    model_version: str
    recommendations: Optional[str] = None
    shap_values: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
