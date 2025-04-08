from litellm import completion
from db import PDFCollectionManager

class LLM:
    def __init__(self, model: str = "ollama/mistral", api_base: str = "http://localhost:11434"):
        self.model = model
        self.api_base = api_base
        self.db = PDFCollectionManager()

    def ask(self, text: str, use_vector_db: bool = True):
        results = []
        context = "Aucun contexte trouvé."

        if use_vector_db:
            print(f"Searching to vector DB...")
            results = self.db.search(text, limit=3)
            context = "\n\n".join([f'## File {r["file"]}: {r["content"]}' for r in results])
        
        system_instruction = """You are an AI specialized as a travel agency assistant.  
        Your task is to answer the user's question based on the provided context, which consists of PDF documents.  
        If the information in the PDFs is not sufficient to provide an accurate answer, you must clearly state that you cannot answer.  
        You may also answer general questions, as long as they relate to travel, trip planning, or finding accommodation.  
        Always respond in the user's language.  
        You must also provide a brief summary or useful information about the property or destination in question,  
        even if this information is already mentioned in the source documents.  
        At the end of each answer, you must cite the sources — specifically the names of the PDF files where the information was found.
        """

        prompt = f"Context: {context}\n\n{system_instruction}"

        print(f"Asking LLM...")
        response = completion(
            model=self.model,
            messages=[
                {"content": prompt, "role": "system"},
                {"content": text, "role": "user"}],
            api_base=self.api_base
        )
        return response.get("choices", [{}])[-1].get("message", {}).get("content", "")

if __name__ == "__main__":
    llm = LLM()
    text = "Trouve moi un hotel proche de la plage."
    response = llm.ask(text)
    print(f"LLM Response: {response}")