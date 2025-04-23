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
            description=(
                "Utilise cet outil pour rechercher des informations dans une base de documents. "
                "Formule les requêtes en FRANÇAIS. "
                "Quand tu utilises cet outil, tu cherches du contexte pour pouvoir répondre. "
                "Ensuite, rédige ta réponse complète en FRANÇAIS pour l'utilisateur. "
                "C'est le SEUL outil disponible pour effectuer des recherches externes."
                "Dans ta reponse finale, tu dois indquer le nom du fichier d'où provient l'information. "
                "Si tu ne trouves pas d'information pertinente, réponds simplement 'Je ne sais pas'. "
            )
        )

        # Définir le LLM
        self.llm = OllamaLLM(model=model_name)

        # Initialiser l'agent
        self.agent = initialize_agent(
            tools=[self.search_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def search_weaviate(self, query: str) -> str:
        """
        Fonction pour rechercher dans Weaviate via le collection_manager.
        """
        response = self.collection_manager.search(query, limit=5)
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
    user_input = """ User: Trouve-moi un hôtel près de la mer. Assistant: Il y a plusieurs hôtels près de la mer dans les résultats de ma recherche. L'un d'eux est l'hôtel Les Roches Rouges qui se trouve en avant d'une île appelée "Île d'Or" et dispose de deux piscines, dont une est un grand bassin d'eau de mer. L'autre hôtel est le BEST WESTERN PLUS LA MARINA situé à 200m des plages de sable fin, du port, du casino, des restaurants, des gares routières et SNCF et des parkings publics. Les chambres de cet hôtel sont non-fumeur et climatisées. Le dernier hôtel est représenté par une brochure, mais aucune information supplémentaire n'est disponible" User: Peux-tu me donner plus de détails sur l'hôtel Les Roches Rouges?"""
    response = agent.run(user_input)
    print(response)
