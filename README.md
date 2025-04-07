# RAG my Theta

## Requirements
- Python 3
- Weaviate
- Docker

## Installation

### Database
You can install Weaviate using Docker. The following command will pull the latest Weaviate image and run it:

```bash
docker run -d -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:1.30.0
```

### Python

Optional: Create a virtual environment to avoid conflicts with other Python packages.
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages using pip :
```bash
pip install -r requirements.txt
```
