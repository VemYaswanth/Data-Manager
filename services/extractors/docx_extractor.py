from docx import Document
import io

def extract_text_from_docx(raw_bytes: bytes) -> str:
    file = io.BytesIO(raw_bytes)
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])
