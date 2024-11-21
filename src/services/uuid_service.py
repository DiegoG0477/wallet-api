import uuid

def generate_uuid() -> str:
    """
    Genera un UUID único en formato string.
    :return: UUID como string
    """
    return str(uuid.uuid4())