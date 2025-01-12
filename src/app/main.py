import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config import *
from src.app.db.database import Base, engine
from src.app.routers import users, voices, auth
from src.app.models.regression import QualityPredictor

app = FastAPI(
    title=APP_NAME,
    version=VERSION
)

@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# app.include_router(users.router, prefix="/api", tags=['Users'])
app.include_router(auth.router, prefix="/api", tags=['Auth'])

if __name__ == "__main__":
    uvicorn.run(
        app="src.app.main:app",
        host="localhost",
        port=8000,
        reload=True,
    )
