# RAG my Theta - Rapport Technique

## Architecture du projet

Ce projet implémente un système de Retrieval-Augmented Generation (RAG) pour une agence de voyages, spécialisé dans la recherche d'informations sur des propriétés à partir de documents PDF. L'architecture se compose de plusieurs composants clés :

1. **Base de données vectorielle** : Weaviate pour le stockage et la recherche des embeddings
2. **Module d'extraction et d'indexation** : Traitement des PDFs et création des embeddings
3. **Module LLM** : Interface avec un modèle de langage (Mistral via Ollama)
4. **API REST** : Exposition des fonctionnalités via FastAPI

## Choix techniques

### Base de données vectorielle

**Technologie** : Weaviate
**Justification** : Weaviate est une base de données vectorielle open-source conçue pour le stockage et la recherche sémantique de données. Facile à déployer via Docker, elle propose une API Python intuitive. L’un de ses atouts majeurs est l’intégration native des embeddings, permettant la vectorisation automatique des documents lors de leur ajout à la base. Cependant, dans le cadre de cet exercice, nous n’utilisons pas cette fonctionnalité, car nous avons besoin d’utiliser des embeddings spécifiques pour le français. Nous avons donc choisi de générer les embeddings en amont, puis de les stocker dans Weaviate.

### Modèle d'embeddings

**Technologie** : BAAI/bge-m3 via Sentence Transformers
**Justification** : Ce modèle offre un excellent rapport qualité/performance pour la création d'embeddings textuels multilangues. Il est particulièrement adapté pour notre cas d'usage qui requiert une bonne compréhension du français.

### Traitement des PDFs

**Technologie** : PyMuPDF (Fitz)
**Justification** : Cette librairie permet d'extraire efficacement le texte de documents PDF tout en étant légère et facile à intégrer.

### LLM

**Technologie** : Mistral via Ollama
**Justification** : Mistral est un modèle de langage open-source performant pour la génération de texte, tout en étant suffisamment léger pour être exécuté localement. Ollama facilite son utilisation grâce à une interface simple. Cependant, pour respecter les consignes de l'exercice qui demandait l'utilisation de ChatGPT-4o, l’API a été développée avec FastAPI, qui interroge Ollama en arrière-plan. Cela signifie que la configuration peut être facilement adaptée pour utiliser ChatGPT-4o à la place de Mistral, si nécessaire.

### API

**Technologie** : FastAPI
**Justification** : FastAPI permet de créer rapidement une interface d’API pour interroger n’importe quel modèle de langage, quel que soit le système sous-jacent. Elle sert ici de pont flexible entre l’application et le modèle utilisé, qu’il s’agisse de Mistral via Ollama ou de ChatGPT-4o.

## Workflow du système

1. **Indexation des documents**
   - Lecture des fichiers PDF du dossier `data`
   - Extraction du texte via PyMuPDF
   - Génération d'embeddings via BAAI/bge-m3
   - Stockage dans Weaviate avec métadonnées (nom du fichier source)

2. **Traitement des requêtes**
   - Réception d'une requête texte via l'API
   - Génération de l'embedding de la requête
   - Recherche des documents similaires dans Weaviate
   - Extraction des documents les plus pertinents
   - Construction d'un prompt enrichi pour le LLM avec le contexte trouvé
   - Génération d'une réponse par le LLM
   - Renvoi de la réponse à l'utilisateur

## Performances et améliorations

Les tests réalisés (voir `tests/results.txt`) montrent que le système est capable de répondre efficacement à des questions sur les propriétés disponibles, en puisant dans les informations contenues dans les PDFs. La qualité des réponses dépend fortement de la qualité des documents indexés et de la pertinence de la recherche vectorielle.

Améliorations possibles :
- Implémentation de techniques de chunking plus avancées pour diviser les documents en segments plus petits
- Ajout d'un système de filtrage pour éliminer les documents non pertinents
- Optimisation des paramètres de recherche vectorielle
- Tests avec d'autres modèles d'embeddings et LLMs
- Mise en place d'un système de feedback pour améliorer les résultats au fil du temps