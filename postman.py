import os
import dotenv
import litellm
import db

DECIDE_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "decide_search",
        "description": "Decides whether a search is needed and which query to use.",
        "parameters": {
            "type": "object",
            "properties": {
                "need_search": {
                    "type": "boolean",
                    "description": "Indicates whether an external search is required."
                },
                "search_query": {
                    "type": "string",
                    "description": "Search query to execute if needed."
                }
            },
            "required": ["need_search", "search_query"]
        }
    }
}

class AIAgent:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        self.api_key = os.getenv("LITELLM_API_KEY")
        self.api_base = os.getenv("LITELLM_API_BASE")
        self.model = os.getenv("LITELLM_API_MODEL")
        self.collection = db.PDFCollectionManager()
        self.local_conversation_history = []

    def chat(self, conversation: list[tuple[str, str]]) -> str:
        self.local_conversation_history = conversation

        # ask the AI to decide if a search is needed
        tool_call = self.decide_search_tool_call()

        # display the decision
        need_search = tool_call.get("need_search", False)
        search_query = tool_call.get("search_query", "")

        if need_search:
            print(f"\033[92mRecherche requise: {search_query}\033[0m")
            context_results = self.collection.search(search_query)
        else:
            print(f"\033[91mPas de recherche requise.\033[0m")
            context_results = []

        # generate the AI's reply based on the context
        assistant_reply = self.generate_reply(context_results)
        self.local_conversation_history.append(("assistant", assistant_reply))

        return assistant_reply

    def decide_search_tool_call(self) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart travel assistant.\n\n"
                    "Your task is to decide whether an external search is required based on the user's last message in the conversation.\n\n"
                    "Always use the `decide_search` function tool when the user is asking about detailed or up-to-date information "
                    "related to travel — like hotels, destinations, trips, transportation, events, beaches, or places that need specific knowledge.\n\n"
                    "Do NOT use the tool if the user is just being social (e.g. saying hello), asking general facts, or saying something common-sense.\n\n"
                    "If a search is needed, set `need_search=true` and provide a concise French search query in `search_query`.\n\n"
                    "Examples:\n"
                    "- User: Bonjour → need_search=false, search_query=''\n"
                    "- User: Peux-tu me recommander un hôtel à Barcelone ? → need_search=true, search_query='hôtel à Barcelone'\n"
                    "- User: Que puis-je visiter à Paris cet été ? → need_search=true, search_query='activités à Paris été'\n"
                    "- User: Quel temps fait-il ? → need_search=false, search_query=''\n"
                    "- User: Salut comment ça va ? → need_search=false, search_query=''\n"
                    "- User: Je cherche un voyage près de la plage → need_search=true, search_query='voyage près de la plage'\n"
                )
            }
        ]

        for role, content in self.local_conversation_history:
            messages.append({"role": role, "content": content})

        try:
            response = litellm.completion(
                model=self.model,
                api_key=self.api_key,
                api_base=self.api_base,
                messages=messages,
                tools=[DECIDE_SEARCH_TOOL],
                tool_choice="auto"
            )

            # Cherche un appel de fonction tool
            tool_calls = response.get("choices", [])[0].get("message", {}).get("tool_calls", [])
            if tool_calls:
                tool_args = tool_calls[0]["function"]["arguments"]
                import json
                return json.loads(tool_args)

        except Exception as e:
            print(f"Erreur durant l'appel LiteLLM: {e}")
            return {"need_search": False, "search_query": ""}

        return {"need_search": False, "search_query": ""}

    def generate_reply(self, context_results: list[dict]) -> str:
        if not context_results:
            return "Aucun contexte généré"

        result = ""
        for doc in context_results:
            file_name = doc.get("file")
            content = doc.get("content", "")
            result += f"### {file_name}\n{content}\n\n"

        return result.strip()


# Exemple d’utilisation
if __name__ == "__main__":
    agent = AIAgent()
    conversation_history = [
        ("user", "Bonjour."),
        ("assistant", "Bonjour! Comment puis-je vous aider aujourd'hui?"),
        ("user", "je cherche un croisiere proche de la mer"),
    ]

    response = agent.chat(conversation_history)
    print(f"Agent: {response}")
