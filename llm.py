import os
import dotenv
from litellm import completion
from postman import AIAgent

class LLM:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        self.api_key = os.getenv("LITELLM_API_KEY")
        self.api_base = os.getenv("LITELLM_API_BASE")
        self.model = os.getenv("LITELLM_API_MODEL")
        if (not self.api_base or not self.model):
            raise ValueError("API base and model must be set in the environment variables.")
        self.postman_agent = AIAgent()
        
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

        print(f"\033[94mPostman reply: {postman_reply}\033[0m")

        try:
            with open("prompts/llm.txt", "r") as file:
                system_instruction = file.read().strip()
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier system prompt: {e}")
            system_instruction = ""
        prompt = f"Context: {postman_reply}\n\n{system_instruction}"

        try:
            response = completion(
                model=self.model,
                messages=[
                    {"content": prompt, "role": "system"},
                    *conversation  # Ajoute tout l'historique
                ],
                api_key=self.api_key,
                api_base=self.api_base,
            )
            llm_reply = response.get("choices", [{}])[-1].get("message", {}).get("content", "")
        except Exception as e:
            print(f"Erreur lors de l'appel au LLM: {e}")
            llm_reply = "Désolé, une erreur technique est survenue lors de la génération de la réponse."
        conversation.append({"role": "assistant", "content": llm_reply})
        return conversation

if __name__ == "__main__":
    llm = LLM()
    text = "Trouve moi un hotel proche de la plage."
    try:
        response = llm.ask(text)
        print(f"LLM Response: {response}")
    except Exception as e:
        print(f"Erreur lors de l'appel à LLM: {e}")