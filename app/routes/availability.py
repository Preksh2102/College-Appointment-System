from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database import get_db
from ..models import Availability
from ..schemas import AvailabilityCreate
from ..routes.users import get_current_user

router = APIRouter()

@router.post("/add")
def add_availability(
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Ensure only professors can add availability
    if not current_user.is_professor:
        raise HTTPException(status_code=403, detail="Only professors can add availability")

    # Validate that professor_id matches the current user's ID from JWT token
    if availability.professor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only add availability for yourself"
        )

    # Validate that start_time is before end_time
    if availability.start_time >= availability.end_time:
        raise HTTPException(status_code=400, detail="start_time must be before end_time")

    # Check for overlapping time slots for the current professor
    overlap = db.query(Availability).filter(
        Availability.professor_id == current_user.id,
        or_(
            and_(Availability.start_time <= availability.start_time, Availability.end_time > availability.start_time),
            and_(Availability.start_time < availability.end_time, Availability.end_time >= availability.end_time),
            and_(Availability.start_time >= availability.start_time, Availability.end_time <= availability.end_time)
        )
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="Overlapping time slot already exists.")

    # Add availability using the validated professor_id
    db_availability = Availability(
        professor_id=current_user.id,  # Use current_user.id for consistency
        start_time=availability.start_time,
        end_time=availability.end_time,
    )
    db.add(db_availability)
    db.commit()

    return {"message": "Availability added successfully."}

@router.get("/{professor_id}")
def get_availability(professor_id: int, db: Session = Depends(get_db)):
    return db.query(Availability).filter_by(professor_id=professor_id).all()

@router.delete("/{availability_id}")
def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Ensure only professors can delete availability
    if not current_user.is_professor:
        raise HTTPException(status_code=403, detail="Only professors can delete availability")

    # Fetch the availability slot
    availability = db.query(Availability).filter_by(id=availability_id).first()

    # Check if the availability exists
    if not availability:
        raise HTTPException(status_code=404, detail="Availability slot not found")

    # Ensure the current user is the professor who owns the availability
    if availability.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own availability slots")

    # Delete the availability slot
    db.delete(availability)
    db.commit()

    return {"message": "Availability slot deleted successfully"}