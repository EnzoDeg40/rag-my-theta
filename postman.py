import litellm
import db

class AIAgent:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.collection = db.PDFCollectionManager()
        self.conversation_history = []  # list of (role, message)

    def chat(self, user_message: str) -> str:
        self.conversation_history.append(("user", user_message))

        # 1. Décider s'il faut faire une recherche
        need_search, search_query = self.decide_search()
        print(f"Need search: {need_search}, Search query: {search_query}")

        context_results = []
        if need_search and search_query:
            context_results = self.collection.search(search_query)

        # 2. Générer une réponse en utilisant le contexte (s'il y en a)
        assistant_reply = self.generate_reply(context_results)

        self.conversation_history.append(("assistant", assistant_reply))

        return assistant_reply

    def decide_search(self) -> tuple[bool, str]:
        prompt = self._build_search_decision_prompt()
        response = litellm.completion(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["choices"][0]["message"]["content"].strip().lower()

        if content.startswith("yes"):
            search_query = content.split("search:", 1)[-1].strip()
            return True, search_query
        else:
            return False, ""

    def generate_reply(self, context_results: list) -> str:
        system_prompt = "You are a helpful AI assistant."
        # context_text = "\n\n".join(context_results) if context_results else ""
        context_text = "\n\n".join([doc.get("content", "") for doc in context_results]) if context_results else ""

        messages = [{"role": "system", "content": system_prompt}]

        for role, message in self.conversation_history:
            messages.append({"role": role, "content": message})

        if context_text:
            messages.append({"role": "system", "content": f"Use the following context to help answer:\n{context_text}"})

        response = litellm.completion(
            model=self.model_name,
            messages=messages
        )

        return response["choices"][0]["message"]["content"].strip()

    def _build_search_decision_prompt(self) -> str:
        formatted_history = "\n".join([
            f"{role}: {message}" for role, message in self.conversation_history
        ])

        return (
            f"Here is the conversation so far:\n{formatted_history}\n\n"
            "Decide if you need to search for external information to better answer.\n"
            "Answer 'Yes' or 'No'.\n"
            "If 'Yes', also specify what to search, and ensure the search query is in French.\n"
            "Format: 'Yes. Search: <search query>' or 'No.'"
        )


# Exemple d'utilisation
if __name__ == "__main__":
    agent = AIAgent(model_name="ollama/mistral")

    while True:
        user_input = input("You: ")
        response = agent.chat(user_input)
        print(f"Assistant: {response}")
