from pydantic import BaseModel
from typing import List

class LevelsResponse(BaseModel):
    levels: List[str]
