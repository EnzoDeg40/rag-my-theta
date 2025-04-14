from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

class ImageDescriber:
    def __init__(self):
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        # Load the BLIP model and processor
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)

    def describe_image(self, image_path: str) -> str:
        # Load and prepare the image
        image = Image.open(image_path).convert('RGB')
        inputs = self.processor(image, return_tensors="pt").to(self.device)

        # Generate a description
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=200)

        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption


if __name__ == "__main__":
    image_file = "Capture d’écran 2025-04-11 à 13.33.31.png"
    describer = ImageDescriber()

    try:
        description = describer.describe_image(image_file)
        print(f"🖼️ Description de l'image : {description}")
    except Exception as e:
        print(f"Erreur : {e}")