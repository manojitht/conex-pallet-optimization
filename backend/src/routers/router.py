from fastapi import APIRouter
from src.models.models import Container, ContainerRequest

router = APIRouter()

@router.post("/load_pallets", summary="Input Pallet dimensions to load into the container")
async def load_pallets(request: ContainerRequest):
    container = Container(request.length, request.width, request.height, request.weight_limit)
    container.load_pallets(request.pallets)
    img_data = container.visualize()
    return {
        "loaded_pallets": container.loaded_pallets,
        "unloaded_pallets": container.unloaded_pallets,
        "visualization": f"data:image/png;base64,{img_data}"
    }