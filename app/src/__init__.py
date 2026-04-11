from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.router import router
import uvicorn

api_version = "v1"

app = FastAPI(title="RapidLink Palletizer Backend App", 
              description="Loading the pallets optimally inside the container.", 
              version=api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=f"/api/{api_version}", tags=["Pallet Loader API"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)