from bs4 import BeautifulSoup

def extract_text_from_html(raw_bytes: bytes) -> str:
    html = raw_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")
