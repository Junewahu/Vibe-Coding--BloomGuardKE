from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    users,
    patients,
    appointments,
    reminders,
    caregivers,
    medical_records,
    auth,
    search,
    sync,
    chw_tracker,
    incentives,
    analytics,
    communications,
    nhif
)
from .database import create_tables, engine, Base
from .config import settings
from .services.task_processor import start_task_processor
from .services.sync_service import sync_service
import asyncio

# Create FastAPI app
app = FastAPI(
    title="BloomGuard API",
    description="Modular Health Platform API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(
    users.router,
    prefix=f"{settings.api_v1_prefix}/users",
    tags=["users"]
)
app.include_router(
    patients.router,
    prefix=f"{settings.api_v1_prefix}/patients",
    tags=["patients"]
)
app.include_router(
    appointments.router,
    prefix=f"{settings.api_v1_prefix}/appointments",
    tags=["appointments"]
)
app.include_router(
    reminders.router,
    prefix=f"{settings.api_v1_prefix}/reminders",
    tags=["reminders"]
)
app.include_router(
    caregivers.router,
    prefix=f"{settings.api_v1_prefix}/caregivers",
    tags=["caregivers"]
)
app.include_router(
    medical_records.router,
    prefix=f"{settings.api_v1_prefix}/medical-records",
    tags=["medical-records"]
)
app.include_router(auth.router)
app.include_router(
    search.router,
    prefix=f"{settings.api_v1_prefix}/search",
    tags=["search"]
)
app.include_router(
    sync.router,
    prefix=f"{settings.api_v1_prefix}/sync",
    tags=["sync"]
)
app.include_router(
    chw_tracker.router,
    prefix=f"{settings.api_v1_prefix}/chw-tracker",
    tags=["chw-tracker"]
)
app.include_router(
    incentives.router,
    prefix=f"{settings.api_v1_prefix}/incentives",
    tags=["incentives"]
)
app.include_router(
    analytics.router,
    prefix=f"{settings.api_v1_prefix}/analytics",
    tags=["analytics"]
)
app.include_router(
    communications.router,
    prefix=f"{settings.api_v1_prefix}/communications",
    tags=["communications"]
)
app.include_router(nhif.router)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    asyncio.create_task(start_task_processor())
    # Start the sync service
    asyncio.create_task(sync_service.start())

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to BloomGuard API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    # Stop the sync service
    await sync_service.stop() 