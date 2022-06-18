import os
import platform
import sys
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
        return_string += str(i) + delimiter
    return return_string


def get_sys_type():
    if sys.platform.startswith('linux'):
        # linux
        return 'linux'

    elif sys.platform.startswith('darwin'):
        # mac os
        return 'osx'

    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        # win
        return 'windows'


def get_sys_bits():
    if platform.architecture()[0] == '64bit':
        return 'x64'
    if platform.architecture()[0] == '32bit':
        return 'x86'


def forge_url(mc_version: str, version: str, branch: str, category: str, forge_format: str) -> str:
    branch = '-{}'.format(branch) if branch else ''
    return 'net/minecraftforge/forge/' + mc_version + '-' + version + branch + '/forge-' + mc_version + '-' \
           + version + branch + '-' + category + '.' + forge_format
