def extract_text_from_csv(raw_bytes: bytes) -> str:
    return raw_bytes.decode("utf-8", errors="ignore")
