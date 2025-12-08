import easyocr
import numpy as np
import cv2

# Initialize reader once to save resources
_reader = easyocr.Reader(["en"])

def extract_text_from_image(raw_bytes: bytes) -> str:
    np_img = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    results = _reader.readtext(img, detail=0)
    return "\n".join(results)
