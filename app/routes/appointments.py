from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Appointment, Availability
from ..schemas import AppointmentCreate
from ..routes.users import get_current_user

router = APIRouter()

@router.post("/book")
def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Handles booking an appointment and adjusting availability accordingly."""

    # Ensure professors cannot book appointments
    if current_user.is_professor:
        raise HTTPException(status_code=403, detail="Professors cannot book appointments.")

    # Validate that student_id matches the current user's ID from JWT token
    if appointment.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only book appointments for yourself"
        )

    # Find the availability slot
    slot = db.query(Availability).filter(
        Availability.professor_id == appointment.professor_id,
        Availability.start_time <= appointment.start_time,
        Availability.end_time >= appointment.end_time
    ).first()

    if not slot:
        raise HTTPException(status_code=404, detail="No available slot for the selected time.")

    # Book the appointment using current_user.id
    db.add(Appointment(
        student_id=current_user.id,  # Use current_user.id for consistency
        professor_id=appointment.professor_id,
        start_time=appointment.start_time,
        end_time=appointment.end_time
    ))

    # Adjust availability based on booking position
    new_availabilities = []

    if slot.start_time < appointment.start_time and slot.end_time > appointment.end_time:
        # Case 1: Student books in the middle -> Split into two availabilities
        new_availabilities.append(Availability(
            professor_id=slot.professor_id,
            start_time=slot.start_time,
            end_time=appointment.start_time
        ))
        new_availabilities.append(Availability(
            professor_id=slot.professor_id,
            start_time=appointment.end_time,
            end_time=slot.end_time
        ))

    elif slot.start_time < appointment.start_time:
        # Case 2: Student books the end -> Adjust end time of availability
        new_availabilities.append(Availability(
            professor_id=slot.professor_id,
            start_time=slot.start_time,
            end_time=appointment.start_time
        ))

    elif slot.end_time > appointment.end_time:
        # Case 3: Student books the start -> Adjust start time of availability
        new_availabilities.append(Availability(
            professor_id=slot.professor_id,
            start_time=appointment.end_time,
            end_time=slot.end_time
        ))

    # Remove the original availability slot
    db.delete(slot)

    # Add new adjusted availability slots
    db.add_all(new_availabilities)
    db.commit()

    return {"message": "Appointment booked successfully."}

@router.put("/cancel/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Ensure only professors can cancel appointments
    if not current_user.is_professor:
        raise HTTPException(status_code=403, detail="Only professors can cancel appointments")

    # Fetch the appointment
    appointment = db.query(Appointment).filter_by(id=appointment_id).first()

    # Check if the appointment exists
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Ensure the professor is the one associated with the appointment
    if appointment.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own appointments")

    # Check if the appointment is already canceled
    if appointment.is_canceled:
        raise HTTPException(status_code=400, detail="Appointment is already canceled")

    # Cancel the appointment
    appointment.is_canceled = True
    db.commit()

    return {"message": "Appointment canceled successfully"}