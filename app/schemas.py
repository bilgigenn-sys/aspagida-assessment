from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AssessmentIn(BaseModel):
    full_name: str = Field(..., min_length=2)
    company: Optional[str] = None
    email: EmailStr
    phone: str = Field(..., pattern=r"^[0-9+\-()\s]{7,20}$")
    tax_id: Optional[str] = Field(None, pattern=r"^[0-9]{10,11}$")
    answers: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

class AssessmentOut(BaseModel):
    id: int
    created_at: str
    full_name: str
    company: Optional[str]
    email: EmailStr
    phone: str
    tax_id: Optional[str]
    answers: Dict[str, Any]
    meta: Optional[Dict[str, Any]]
    pdf_path: Optional[str]

class SMTPIn(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True

class SMTPOut(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    use_tls: bool

class StatsOut(BaseModel):
    total_tests: int
    todays_tests: int
    companies: int
