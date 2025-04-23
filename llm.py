from litellm import completion
from db import PDFCollectionManager
from postman import AIAgent

class LLM:
    def __init__(self, model: str = "ollama/mistral", api_base: str = "http://localhost:11434"):
        self.model = model
        self.api_base = api_base
        self.postman_agent = AIAgent(model_name="ollama/mistral")

    def handle_conversation(self, conversation: list[dict]) -> list[dict]:
        # Trouver le dernier message utilisateur
        last_user_message = None
        for msg in reversed(conversation):
            if msg.get("role") == "user":
                last_user_message = msg["content"]
                break
        if not last_user_message:
            # Rien à faire si pas de message utilisateur
            return conversation

        postman_reply = self.postman_agent.chat([(m["role"], m["content"]) for m in conversation])

        with open("prompts/llm.txt", "r") as file:
            system_instruction = file.read().strip()
        prompt = f"Context: {postman_reply}\n\n{system_instruction}"

        response = completion(
            model=self.model,
            messages=[
                {"content": prompt, "role": "system"},
                *conversation  # Ajoute tout l'historique
            ],
            api_base=self.api_base
        )
        llm_reply = response.get("choices", [{}])[-1].get("message", {}).get("content", "")
        conversation.append({"role": "assistant", "content": llm_reply})
        return conversation

if __name__ == "__main__":
    llm = LLM()
    text = "Trouve moi un hotel proche de la plage."
    response = llm.ask(text)
    print(f"LLM Response: {response}")