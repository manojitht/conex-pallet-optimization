from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import router

app = FastAPI(title="Container Pallet Optimization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "running"}
