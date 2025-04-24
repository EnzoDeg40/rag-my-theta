# RAG my Theta - Rapport Technique

## Architecture du projet

Ce projet implémente un système de Retrieval-Augmented Generation (RAG) pour une agence de voyages, spécialisé dans la recherche d'informations sur des propriétés à partir de documents PDF. L'architecture se compose de plusieurs composants clés :

1. **Base de données vectorielle** : Weaviate pour le stockage et la recherche des embeddings
2. **Module d'extraction et d'indexation** : Traitement des PDFs et création des embeddings
3. **Module LLM** : Interface avec un modèle de langage (Mistral via Ollama)
4. **Agent de recherche** : Un agent dédié gère la recherche d'informations dans la base de données vectorielle
5. **API REST** : Exposition des fonctionnalités via FastAPI

## Choix techniques

### Base de données vectorielle

**Technologie** : Weaviate
**Justification** : Weaviate est une base de données vectorielle open-source conçue pour le stockage et la recherche sémantique de données. Facile à déployer via Docker, elle propose une API Python intuitive. L’un de ses atouts majeurs est l’intégration native des embeddings, permettant la vectorisation automatique des documents lors de leur ajout à la base. Cependant, dans le cadre de cet exercice, nous n’utilisons pas cette fonctionnalité, car nous avons besoin d’utiliser des embeddings spécifiques pour le français. Nous avons donc choisi de générer les embeddings en amont, puis de les stocker dans Weaviate.

### Modèle d'embeddings

**Technologie** : BAAI/bge-m3 via Sentence Transformers
**Justification** : Ce modèle offre un excellent rapport qualité/performance pour la création d'embeddings textuels multilingues. Il est particulièrement adapté à notre cas d'usage qui requiert une bonne compréhension du français.

### Modèle de vision
**Technologie** : Salesforce/blip-image-captioning-large  
**Justification** : Ce modèle est conçu pour générer des descriptions d'images de haute qualité. Il est particulièrement utile pour extraire des informations visuelles pertinentes des premières pages des documents PDF, comme des images ou des graphiques, afin d'enrichir les métadonnées stockées dans la base de données vectorielle. Sa précision et sa capacité à comprendre le contexte visuel en font un choix idéal pour ce projet.

### Découpage des tokens
**Technologies** : NLTK, tiktoken
**Justification** : Les textes des PDF sont segmentés en phrases à l’aide de nltk, puis ces phrases sont regroupées en blocs ne dépassant pas un certain nombre de tokens (50 ici), mesurés avec tiktoken. Cela permet de gérer efficacement la taille des prompts envoyés au modèle de langage tout en préservant le sens du texte. 

### Traitement des PDFs

**Technologie** : PyMuPDF (Fitz)
**Justification** : Cette librairie permet d'extraire efficacement le texte de documents PDF tout en étant légère et facile à intégrer.

### LLM

**Technologie** : Mistral via Ollama
**Justification** : Mistral est un modèle de langage open-source performant pour la génération de texte, tout en étant suffisamment léger pour être exécuté localement. Ollama facilite son utilisation grâce à une interface simple. Cependant, pour respecter les consignes de l'exercice qui demandaient l'utilisation de ChatGPT-4o, l’API a été développée avec FastAPI, qui interroge Ollama en arrière-plan. Cela signifie que la configuration peut être facilement adaptée pour utiliser ChatGPT-4o à la place de Mistral, si nécessaire.

### Agent de recherche

**Technologie** : Python
**Justification** : L'agent de recherche est un module Python qui peut rechercher des informations dans la base de données vectorielle. À partir de la conversation entre le LLM et l'utilisateur, il décide si une recherche documentaire est nécessaire. Il interroge ensuite Weaviate pour récupérer les documents pertinents. Ce module est essentiel pour enrichir le contexte de la réponse générée par le LLM. J'avais essayé d'utiliser LangChain pour cette partie, mais beaucoup de choses n'étaient pas modulables et je n'ai pas pu l'adapter à mes besoins. J'ai donc décidé de créer un module Python sur mesure qui répond à mes besoins.

### API

**Technologie** : FastAPI
**Justification** : FastAPI permet de créer rapidement une interface d’API pour interroger n’importe quel modèle de langage, quel que soit le système sous-jacent. Elle sert ici de pont flexible entre l’application et le modèle utilisé, qu’il s’agisse de Mistral via Ollama ou de ChatGPT-4o.

## Workflow du système

1. **Indexation des documents**
   - Lecture des fichiers PDF du dossier `data`
   - Extraction du texte via PyMuPDF
   - Découpage du texte en segments d'environ 50 tokens
   - Génération d'embeddings via BAAI/bge-m3
   - Description des 3 premières images avec un modèle de vision
   - Stockage dans Weaviate avec métadonnées (nom du fichier source)

2. **Traitement des requêtes**
   - Réception d'une requête texte via l'API
   - Le module LLM analyse l'historique de la conversation
   - Il sollicite l'agent de recherche (postman.py) pour décider s'il faut effectuer une recherche documentaire
   - Si oui, l'agent interroge Weaviate et prépare un contexte pertinent
   - Le LLM construit un prompt enrichi avec ce contexte et génère une réponse
   - La réponse est renvoyée à l'utilisateur

## Performances et améliorations

Le test réalisé (voir `tests/result.md`) montre que le système est capable de répondre efficacement à des questions sur les propriétés disponibles, en puisant dans les informations contenues dans les PDFs. La qualité des réponses dépend fortement de la qualité des documents indexés et de la pertinence de la recherche vectorielle effectuée par l'agent.

Améliorations possibles :
- Ajout d'un système de filtrage pour éliminer les documents non pertinents
- Optimisation des paramètres de recherche vectorielle
- Mise en place d'un système de feedback pour améliorer les résultats au fil du temps