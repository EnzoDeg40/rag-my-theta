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
    response = requests.post(
        "http://127.0.0.1:8000/conversation",
        json={"conversation": conversation}
    )
    
    # Ajouter la réponse de l'API à la conversation
    if response.status_code == 200:
        api_response = response.json()
        last_msg = api_response[-1]
        print(f"{last_msg['role']}: {last_msg['content']}\n")
        conversation = api_response  # On garde la conversation à jour
    else:
        print("Erreur lors de la communication avec l'API.")
    
    

# print("Nouvelle conversation :")
# for msg in response.json():
#     print(f"{msg['role']}: {msg['content']}\n")