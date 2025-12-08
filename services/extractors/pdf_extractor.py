import fitz  # PyMuPDF
import io

def extract_text_from_pdf(raw_bytes: bytes) -> str:
    text = []
    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)
