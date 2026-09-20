import os
from dotenv import load_dotenv

# Explicitly load from backend/.env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import profile, state, forecast, simulate, strategy, copilot
from .core import database

# Create tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BankOS MVP API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(profile.router)
app.include_router(state.router)
app.include_router(forecast.router)
app.include_router(simulate.router)
app.include_router(strategy.router)
app.include_router(copilot.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to BankOS API"}

from .services.automation import start_automation_daemon

@app.on_event("startup")
def on_startup():
    start_automation_daemon()
