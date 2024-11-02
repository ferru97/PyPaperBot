def URLjoin(*args):
    return "/".join(map(lambda x: str(x).rstrip('/'), args))