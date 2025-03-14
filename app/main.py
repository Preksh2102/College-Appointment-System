from fastapi import FastAPI
from app.database import engine, Base  # Use absolute import to avoid issues
from app.routes import appointments, users, availability  # Ensure these modules exist

# Ensure database tables are created before the application starts
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Include route files
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(availability.router, prefix="/availability", tags=["availability"])

@app.get("/")
def root():
    return {"message": "Welcome to College Appointment System"}
