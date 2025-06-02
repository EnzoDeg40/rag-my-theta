from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self, model_name="BAAI/bge-reranker-v2-m3"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[str]) -> list[tuple[float, str]]:
        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)
        reranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return reranked
    
if __name__ == "__main__":
    reranker = CrossEncoderReranker()
    query = "Quels sont les meilleurs itinéraires pour un safari en Afrique de l'Est en famille avec enfants, incluant des conseils de sécurité et des recommandations d'hébergements adaptés ?"
    documents = [
        "Découvrez les plus beaux safaris en Afrique de l'Est, avec des conseils pour voyager avec des enfants en toute sécurité et des hébergements familiaux recommandés.",
        "Guide complet pour organiser un safari en solo en Afrique australe, incluant les parcs nationaux incontournables.",
        "Top 10 des hôtels de luxe en Afrique du Sud pour les couples en lune de miel.",
        "Conseils pratiques pour voyager avec des enfants en Afrique : sécurité, santé et activités adaptées.",
        "Itinéraires de safari en Tanzanie et au Kenya, avec recommandations d'hébergements pour familles et astuces pour un voyage serein avec des enfants.",
        "Voyager en Afrique : comment choisir entre safari, plage et découverte culturelle ?",
        "Les meilleures destinations pour un safari photo en Afrique, avec ou sans guide.",
    ]

    reranked_results = reranker.rerank(query, documents)
    for score, doc in reranked_results:
        print(f"Score: {score:.4f} | Document: {doc}")