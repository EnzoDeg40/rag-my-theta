import os
import litellm
import dotenv
import re
import db
class AIAgent:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        self.api_key = os.getenv("LITELLM_API_KEY")
        self.api_base = os.getenv("LITELLM_API_BASE")
        self.model = os.getenv("LITELLM_API_MODEL")
        self.collection = db.PDFCollectionManager()
        self.local_conversation_history = []
        
    def chat(self, conversation: list[dict]) -> str:
        self.local_conversation_history = conversation

        need_search, search_query = self.decide_search()
        if need_search is True:
            print(f"\033[92mNeed search: {need_search}, Search query: {search_query}\033[0m")  # Green
        elif need_search is False:
            print(f"\033[91mNeed search: {need_search}, Search query: {search_query}\033[0m")  # Red
        else:
            print(f"\033[93mNeed search: {need_search}, Search query: {search_query}\033[0m")  # Yellow

        context_results = []
        if need_search and search_query:
            context_results = self.collection.search(search_query)

        # 2. Générer une réponse en utilisant le contexte (s'il y en a)
        assistant_reply = self.generate_reply(context_results)

        self.local_conversation_history.append(("assistant", assistant_reply))

        return assistant_reply


    def get_first_clean_word(self, text: str) -> str:
        text = text.lstrip("#. -_")
        match = re.search(r'\b\w+\b', text)
        if match:
            return match.group(0).lower()
        return ""

    def decide_search(self) -> tuple[bool, str]:
        prompt = self._build_search_decision_prompt()
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
            api_base=self.api_base,
        )

        content = response["choices"][0]["message"]["content"].strip().lower()
        print(f"\033[94mDecision content: {content}\033[0m")  # Blue

        if self.get_first_clean_word(content) == "yes":
            search_query = content.split("search:", 1)[-1].strip()
            return True, search_query
        else:
            return False, ""

    def generate_reply(self, context_results: list) -> str:
        if not context_results:
            return ""

        result = ""
        for doc in context_results:
            file_name = doc.get("file")
            content = doc.get("content", "")
            result += f"### {file_name}\n{content}\n\n"

        return result.strip()

    def _build_search_decision_prompt(self) -> str:
        formatted_history = "\n".join([
            f"### {role}\n{message}\n" for role, message in self.local_conversation_history
        ])
        
        print(f"\033[93m{formatted_history}\033[0m")
        
        return (
            f"Here is the conversation so far:\n{formatted_history}\n\n"
            "Decide whether you need to perform an external search to provide a better answer.\n"
            "Answer 'Yes' or 'No'.\n"
            "The conversation helps to better understand what to look for but you should decide only from the user's last message.\n"
            "\n"
            "Say 'Yes' if the user is asking for detailed or up-to-date information about a trip, hotel, transports, destination, or travel-related topic that requires specific knowledge.\n"
            "Say 'No' if the user is just making casual conversation (e.g., greetings, general questions like the weather today, or common knowledge).\n"
            "\n"
            "If 'Yes', also specify what to search, and ensure the search query is in French.\n"
            "Format: 'Yes. Search: <search query>' or 'No.'"
        )



# Exemple d'utilisation
if __name__ == "__main__":
    agent = AIAgent(model_name="ollama/llama3.1")
    conversation_history = [
        ("user", "Bonjour."),
        ("assistant", "Bonjour! Comment puis-je vous aider aujourd'hui?"),
        ("user", "je cherche un hôtel près de la plage.")
    ]

    response = agent.chat(conversation_history)
    print(f"Agent: {response}")

    # while True:
    #     user_input = input("You: ")
    #     response = agent.chat(user_input)
    #     print(f"Assistant: {response}")
