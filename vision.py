from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

class ImageDescriber:
    def __init__(self):
        try:
            self.device = self._get_device()
            print(f"Using device for {__class__.__name__}: {self.device}")

            # Load the BLIP model and processor
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)
        except Exception as e:
            print(f"Erreur lors du chargement du modèle BLIP: {e}")
            raise
    
    def _get_device(self):
        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")

    def describe_image(self, image) -> str:
        try:
            if not image.mode == 'RGB':
                image = image.convert('RGB')
            text = "an image of "
            inputs = self.processor(image, text, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_new_tokens=200)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"Erreur lors de la description de l'image: {e}")
            return ""

if __name__ == "__main__":
    image_file = "Capture d’écran 2025-04-11 à 13.33.31.png"
    try:
        describer = ImageDescriber()
        with Image.open(image_file) as img:
            description = describer.describe_image(img)
        print(f"🖼️ Description de l'image : {description}")
    except Exception as e:
        print(f"Erreur : {e}")