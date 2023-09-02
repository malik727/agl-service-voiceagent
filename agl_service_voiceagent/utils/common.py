
def add_trailing_slash(path):
    if path and not path.endswith('/'):
        path += '/'
    return path