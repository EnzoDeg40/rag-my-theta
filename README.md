# RAG my Theta

## Requirements
- Python 3
- Weaviate
- Docker
- LiteLLM

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

### LiteLLM

A `.env.template` file is available in the project. Duplicate it and rename the copy to `.env`. Then, fill in the required environment variables as specified in the template.
```
cp .env.template .env
nano .env
```

## Usage

Place your PDF files in the `data` folder at the root of the project. Then, inject them into the vector database using the following command:

```bash
python integration.py
```

Run the following command to start the API server:
```bash
uvicorn api:app
```

To test the API, you can use the following command:
```bash
./request.bash "<your_query>"
```

## Report

View the technical report in French [here](rapport.md)