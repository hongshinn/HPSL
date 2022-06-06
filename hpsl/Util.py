import os


def path_conversion(base_path: str, path: str) -> str:
    return_path = base_path
    for path_fragment in path.split('/'):
        return_path = os.path.join(return_path, path_fragment)
    return return_path
