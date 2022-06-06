import os
import zipfile


def path_conversion(base_path: str, path: str) -> str:
    return_path = base_path
    for path_fragment in path.split('/'):
        return_path = os.path.join(return_path, path_fragment)
    return return_path


def un_zip(file_name: str, save_path: str):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(save_path):
        pass
    else:
        os.makedirs(save_path)
    for names in zip_file.namelist():
        zip_file.extract(names, save_path)
    zip_file.close()


def list2str(input_list: list, delimiter: str) -> str:
    return_string = ''
    for i in input_list:
        return_string += str(i)+delimiter
    return return_string
