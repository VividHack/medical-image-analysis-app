from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from backend.api import authentication, predictions, users
from backend.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Image Analysis API")

# Configure CORS
# In production, replace with specific origins of your frontend application
frontend_url = os.getenv("FRONTEND_URL")
allow_origins = ["localhost:3000"] # local frontend development
if frontend_url:
    allow_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(authentication.router, tags=["Authentication"], prefix="/api")
app.include_router(users.router, tags=["Users"], prefix="/api/users")
app.include_router(predictions.router, tags=["Predictions"], prefix="/api/predictions")

# Mount static files
app.mount("/static", StaticFiles(directory="backend/public"), name="static")

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Medical Image Analysis API"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) 