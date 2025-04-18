from langchain_community.tools import Tool
from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
# import weaviate
import db

# Connexion à Weaviate
# client = weaviate.connect_to_local()  # ou ton endpoint distant selon config

collection_manager = db.PDFCollectionManager()

# 1. Définir une fonction pour chercher dans Weaviate
def search_weaviate(query: str) -> str:
    """
    Fonction appelée par l'agent pour faire une recherche vectorielle dans Weaviate
    """
    # response = (
    #     client.collections.get("YourCollectionName")
    #     .query
    #     .near_text(query=query, limit=3)
    # )
    response = collection_manager.search(query, limit=3)
    
    results = []
    for res in response:
        # On peut formater les résultats comme on veut
        results.append(f"## Fichier: {res['file']}\n\n{res['content']}")
    
    return "\n\n".join(results) if results else "Aucun résultat trouvé."

# 2. Définir le Tool LangChain qui encapsule cette fonction
search_tool = Tool(
    name="SearchWeaviate",
    func=search_weaviate,
    description="Utiliser cet outil pour chercher des informations si besoin de contexte externe."
)

# 3. Définir ton LLM
llm = OllamaLLM(model="mistral", temperature=0)

# 4. Initialiser l'agent
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Agent basique qui sait réfléchir/agir
    verbose=True  # pour voir ce qu'il fait
)

# 5. Utiliser l'agent pour répondre
user_input = "Trouve-moi un hôtel près de la mer"
response = agent.invoke(user_input)

print(response)
