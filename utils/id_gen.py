"""utils/id_gen.py - Generates short unique IDs for ledger objects."""
import uuid


def generate_id() -> str:
    """Return an 8-character UUID hex string."""
    return str(uuid.uuid4())[:8]
