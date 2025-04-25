import requests

conversation = []

while True:
    user_input = input("Vous: ")
    if user_input.lower() == "exit":
        break
    if user_input.lower() == "show_json":
        print(conversation)
        continue
    if not user_input.strip():
        continue

    # Ajouter le message de l'utilisateur à la conversation
    conversation.append({"role": "user", "content": user_input})

    # Envoyer la conversation à l'API
    try:
        response = requests.post(
            "http://127.0.0.1:8000/conversation",
            json={"conversation": conversation},
            timeout=30,
        )
        if response.status_code == 200:
            try:
                api_response = response.json()
                last_msg = api_response[-1]
                print(f"{last_msg['role']}: {last_msg['content']}\n")
                conversation = api_response  # On garde la conversation à jour
            except Exception as e:
                print(f"Erreur lors du décodage de la réponse JSON: {e}")
        else:
            print(f"Erreur lors de la communication avec l'API. Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Erreur réseau lors de la requête HTTP: {e}")