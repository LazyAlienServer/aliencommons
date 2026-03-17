import uuid


def unique_suffix():
    """
    Generates a unique 8-digit suffix.
    """
    return uuid.uuid4().hex[:8]
