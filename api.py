from fastapi import FastAPI
from pydantic import BaseModel
from llm import LLM
from typing import List, Dict

app = FastAPI()
ai = LLM()

class InputData(BaseModel):
    text: str

class ConversationData(BaseModel):
    conversation: List[Dict[str, str]]

@app.post("/conversation", response_model=List[Dict[str, str]])
def process_conversation(data: ConversationData):
    print("Processing conversation...")
    updated_conversation = ai.handle_conversation(data.conversation)
    print(f"Updated Conversation: {updated_conversation}")
    return updated_conversation
