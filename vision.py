from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

def describe_image(image_path: str):
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    # Charger le modèle BLIP + processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)

    # Charger et préparer l'image
    image = Image.open(image_path).convert('RGB')
    inputs = processor(image, return_tensors="pt").to(device)

    # Générer une description
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=200)

    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

if __name__ == "__main__":
    image_file = "Capture d’écran 2025-04-11 à 13.33.31.png"

    try:
        description = describe_image(image_file)
        print(f"🖼️ Description de l'image : {description}")
    except Exception as e:
        print(f"Erreur : {e}")