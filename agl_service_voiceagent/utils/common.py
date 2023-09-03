import uuid


def add_trailing_slash(path):
    if path and not path.endswith('/'):
        path += '/'
    return path

def generate_unique_uuid(length):
    unique_id = str(uuid.uuid4().int)
    # Ensure the generated ID is exactly 'length' digits by taking the last 'length' characters
    unique_id = unique_id[-length:]
    return unique_id