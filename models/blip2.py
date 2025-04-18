from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

class ImageCaptioning:
    def __init__(self):
        """ Load the BLIP-2 model and processor """
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def generate_caption(self, image_path):
        """ Generate caption from the input image """
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(image, return_tensors="pt")
        output = self.model.generate(**inputs)
        caption = self.processor.decode(output[0], skip_special_tokens=True)
        return caption
