from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import pandas as pd
import io

from src.models.models import ContainerOptimizer

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/api/optimize")
async def optimize_container(
    algorithm: str = Form(...),
    containerSize: str = Form(...),
    dataset: UploadFile = File(...)
):
    contents = await dataset.read()
    df = pd.read_csv(io.BytesIO(contents))
    pallets = df.to_dict('records')
    
    c_length, c_width, c_height, c_weight = map(int, containerSize.split(','))
    
    optimizer = ContainerOptimizer(
        length=c_length, 
        width=c_width, 
        height=c_height, 
        weight_limit=c_weight
    )
    
    if algorithm == "greedy":
        results = optimizer.greedy_heuristic(pallets)
    elif algorithm == "milp":
        results = {"error": "MILP not yet implemented"}
    elif algorithm == "genetic":
        results = {"error": "Genetic Algorithm not yet implemented"}
        
    return JSONResponse(content=results)