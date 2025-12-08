from services.embedding_service import embed_text
from services.text_extraction_service import extract_text_from_bytes

def build_answer(query: str, memory: list, files: list):
    """
    Combine:
    - conversation memory
    - relevant files
    - semantic reranking
    """

    context_text = "\n".join([f"{m['role']}: {m['content']}" for m in memory])

    # Combine memory + current query
    combined_query = f"{context_text}\n\nUser question: {query}"

    # Produce a ranked list
    ranked = sorted(files, key=lambda f: f.get("score", 0), reverse=True)

    if not ranked:
        return ("I couldn't find any documents matching this.", [])

    # Build summary answer
    answer_parts = []
    used_sources = []

    for f in ranked[:3]:  # use only top 3
        snippet = f"File: {f['name']} (v{f['version']})"
        answer_parts.append(f"- {snippet}")
        used_sources.append(f["name"])

    answer_text = (
        f"Based on your question and conversation memory, here is what I found:\n\n"
        + "\n".join(answer_parts)
        + "\n\nLet me know if you want detailed content from any file."
    )

    return answer_text, used_sources
