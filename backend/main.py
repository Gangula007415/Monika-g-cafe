from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from backend.database import engine, Base, auto_migrate_schema
from backend.models import User

from backend.routers import (
    auth,
    menu,
    orders,
    billing,
    inventory,
    employees,
    customer,
    reservation,
    feedback,
    reports,
)

import os


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables & auto migrate missing columns
    try:
        Base.metadata.create_all(bind=engine)
        auto_migrate_schema()
    except Exception as e:
        print(f"⚠️ Database initialization warning (DB may be offline or initializing): {e}")
    yield


# Create FastAPI application
app = FastAPI(
    title="Monika G Cafe Management System API",
    lifespan=lifespan
)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(billing.router)
app.include_router(inventory.router)
app.include_router(employees.router)
app.include_router(customer.router)
app.include_router(reservation.router)
app.include_router(feedback.router)
app.include_router(reports.router)


# Frontend static files path
frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "frontend")
)


if os.path.exists(frontend_path):

    @app.get("/")
    def read_root():
        return RedirectResponse(url="/login.html")


    app.mount(
        "/",
        StaticFiles(directory=frontend_path, html=True),
        name="static"
    )