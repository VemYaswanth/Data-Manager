# services/memory_service.py

from collections import defaultdict

# conversation_id -> list of messages
CONVERSATIONS = defaultdict(list)

# pinned memory (per conversation or global)
PINNED = defaultdict(list)

MAX_MEMORY = 10  # short-term window


def add_message(conversation_id: str, role: str, content: str):
    """Store a new message into a conversation."""
    CONVERSATIONS[conversation_id].append({"role": role, "content": content})

    # Trim
    if len(CONVERSATIONS[conversation_id]) > MAX_MEMORY:
        CONVERSATIONS[conversation_id].pop(0)


def get_memory(conversation_id: str):
    """Return merged pinned + short-term memory."""
    pinned = PINNED.get(conversation_id, [])
    recent = CONVERSATIONS.get(conversation_id, [])[-MAX_MEMORY:]
    return pinned + recent


def reset_memory(conversation_id: str):
    """Clear short-term conversation memory but keep pinned notes."""
    CONVERSATIONS[conversation_id].clear()


def reset_all_memory(conversation_id: str):
    """Clear EVERYTHING including pinned memory."""
    CONVERSATIONS[conversation_id].clear()
    PINNED[conversation_id].clear()


def pin_message(conversation_id: str, content: str):
    """Store a pinned memory item."""
    PINNED[conversation_id].append({"role": "system", "content": content})
