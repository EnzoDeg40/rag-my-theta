from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from db import PDFCollectionManager

app = FastAPI()
db = PDFCollectionManager()

class InputData(BaseModel):
    text: str

class SearchResult(BaseModel):
    content: str
    file: str
    distance: float
    
@app.post("/hotels", response_model=List[SearchResult])
def process_text(data: InputData):
    results = db.search(data.text)
    return results
