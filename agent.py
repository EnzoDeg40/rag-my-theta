from langchain_community.tools import Tool
from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
import db


class WeaviateAgent:
    def __init__(self, model_name="mistral", temperature=0):
        # Connexion au gestionnaire de collection (Weaviate abstrait)
        self.collection_manager = db.PDFCollectionManager()

        # Définir le Tool
        self.search_tool = Tool(
            name="SearchWeaviate",
            func=self.search_weaviate,
            description="Utiliser cet outil pour chercher des informations si besoin de contexte externe."
        )

        # Définir le LLM
        self.llm = OllamaLLM(model=model_name, temperature=temperature)

        # Initialiser l'agent
        self.agent = initialize_agent(
            tools=[self.search_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def search_weaviate(self, query: str) -> str:
        """
        Fonction pour rechercher dans Weaviate via le collection_manager.
        """
        response = self.collection_manager.search(query, limit=3)
        results = []
        for res in response:
            results.append(f"## Fichier: {res['file']}\n\n{res['content']}")
        return "\n\n".join(results) if results else "Aucun résultat trouvé."

    def run(self, user_input: str) -> str:
        """
        Utiliser l'agent pour répondre à un input utilisateur.
        """
        return self.agent.invoke(user_input)


if __name__ == "__main__":
    agent = WeaviateAgent()
    user_input = "Trouve-moi un hôtel près de la mer"
    response = agent.run(user_input)
    print(response)
