from litellm import completion

class LLM:
    def __init__(self, model: str = "ollama/mistral", api_base: str = "http://localhost:11434"):
        self.model = model
        self.api_base = api_base

    def ask(self, text: str, use_vector_db: bool = True):
        response = completion(
            model=self.model,
            messages=[{"content": text, "role": "user"}],
            api_base=self.api_base
        )
        return response

if __name__ == "__main__":
    llm = LLM()
    text = "What is the purpose of the document?"
    response = llm.ask(text)
    print(f"LLM Response: {response}")