import requests
import json

# Liste des prompts de test
with open("prompts.txt", "r", encoding="utf-8") as file:
    prompts = [line.strip() for line in file if line.strip()]

# Endpoint de l'API FastAPI
api_url = "http://localhost:8000/hotels"

def test_prompts(prompts):
    for prompt in prompts:
        print(f"Utilisateur:\n{prompt}\n")

        payload = {"text": prompt}
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://127.0.0.1:8000/hotels", headers=headers, data=json.dumps(payload))

        print(f"Réponse LLM: {response.status_code}\n{response.text}\n\n")
        print("-" * 50)

if __name__ == "__main__":
    test_prompts(prompts)
