from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from db import PDFCollectionManager

app = FastAPI()
db = PDFCollectionManager()

class InputData(BaseModel):
    text: str

@app.post("/hotels", response_model=List[str])
def process_text(data: InputData):
    words = data.text.split()
    return words
