from fastapi import FastAPI
from pydantic import BaseModel
from llm import LLM

app = FastAPI()
ai = LLM()

class InputData(BaseModel):
    text: str

@app.post("/hotels", response_model=str)
def process_text(data: InputData):
    print("Processes the client's request...")
    response = ai.ask(data.text)
    print(f"LLM Response: {response}")
    return str(response)
