from pydantic import BaseModel
from typing import List, Optional

# Pesticide Model
class Pesticide(BaseModel):
    name: str
    url: str

# Disease Model (Used for RAG)
class Disease(BaseModel):
    id: str
    disease_name: str
    crop: str
    description: str
    causes: str
    symptoms: str
    solution: str
    prevention: str
    pesticides: List[Pesticide]

# User → Backend Chat Request
class ChatRequest(BaseModel):
    message: str
    language: str = "English"
    cnn_prediction: Optional[int] = None   # 0=Healthy, 1=Diseased (for now)

# Backend → Frontend Chat Response
class ChatResponse(BaseModel):
    response: str
    source_diseases: List[Disease]
    language: str
