from pydantic import BaseModel
from typing import List

class Pallet(BaseModel):
    pallet_id: str
    length: int
    width: int
    height: int
    weight: int
    quantity: int

class ContainerRequest(BaseModel):
    length: int
    width: int
    height: int
    weight_limit: int
    pallets: List[Pallet]

