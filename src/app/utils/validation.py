from datetime import datetime
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, validator
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session


# Types et modèles Pydantic
class ModelFeatures(BaseModel):
    sender: str
    message: Optional[str]=None
    model_type: Literal["classification", "regression"]
    algorithm: str
    features: Dict[str, float]