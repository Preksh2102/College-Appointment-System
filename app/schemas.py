from pydantic import BaseModel
from datetime import datetime

class TokenData(BaseModel):
    username: str

class UserCreate(BaseModel):
    username: str
    password: str
    is_professor: bool

class AvailabilityCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    professor_id: int

class AppointmentCreate(BaseModel):
    student_id: int  # Added this line
    professor_id: int
    start_time: datetime
    end_time: datetime
