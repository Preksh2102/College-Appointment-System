from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_professor = Column(Boolean, default=False)


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)  # Replaced time_slot with start_time
    end_time = Column(DateTime)  # Added end_time


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    professor_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)  # Start time of the appointment
    end_time = Column(DateTime)  # End time of the appointment
    is_canceled = Column(Boolean, default=False)  # New field to track cancellation status