import cv2
import easyocr
from typing import List, Dict, Union


class OCRService:
    def __init__(self, languages: List[str] = ['en']):
        """
        Initialize the OCRService with EasyOCR.
        :param languages: List of language codes for EasyOCR (default: ['en'])
        """
        self.reader = easyocr.Reader(languages)

    def image_to_text(self, image_path: str) -> str:
        """
        Extracts plain text from the given image.
        :param image_path: Path to the image file
        :return: Recognized text as a single string
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        results = self.reader.readtext(image)
        text = " ".join([text for (_, text, _) in results])
        return text.strip()

    def image_to_detailed_text(self, image_path: str) -> List[Dict[str, Union[str, float, list]]]:
        """
        Extracts detailed OCR data including bounding boxes and confidence scores.
        :param image_path: Path to the image file
        :return: List of dictionaries with text, confidence, and bounding box
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        results = self.reader.readtext(image)
        detailed_data = []
        for (bbox, text, prob) in results:
            detailed_data.append({
                "text": text,
                "confidence": round(prob, 2),
                "bounding_box": bbox
            })
        return detailed_data

    def visualize_text(self, image_path: str, output_path: str = None):
        """
        Draws bounding boxes and recognized text on the image for visualization.
        :param image_path: Path to the input image
        :param output_path: Optional path to save the output image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        results = self.reader.readtext(image)
        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(image, text, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        if output_path:
            cv2.imwrite(output_path, image)
        else:
            cv2.imshow("Recognized Text", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

# from transformers import TrOCRProcessor, VisionEncoderDecoderModel
# from PIL import Image
#
# class OCRService:
#     def __init__(self):
#         self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
#         self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
#
#     def image_to_text(self, image_path: str) -> str:
#         image = Image.open(image_path).convert("RGB")
#         pixel_values = self.processor(images=image, return_tensors="pt").pixel_values
#         generated_ids = self.model.generate(pixel_values)
#         text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#         return text.strip()
#
#
# # import easyocr
# #
# # class OCRService:
# #     def __init__(self):
# #         self.reader = easyocr.Reader(['en'])
# #
# #     def image_to_text(self, image_path: str) -> str:
# #         result = self.reader.readtext(image_path, detail=0)
# #         return " ".join(result)
# #
# #
#
#
# # from PIL import Image
#
#
#
# # import pytesseract
# #
# #
# # class OCRService:
# #     def __init__(self):
# #         pass
# #
# #     def image_to_text(self, image_path: str) -> str:
# #         img = Image.open(image_path)
# #         text = pytesseract.image_to_string(img)
# #         print(text)
# #         return text.strip()
