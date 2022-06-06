import json
import os
import hpsl.Network
import sys
import platform
import hashlib


class Download:
    def __init__(self):
        self.bmclapi = {'http://launchermeta.mojang.com/': 'https://bmclapi2.bangbang93.com/',
                        'https://launcher.mojang.com/': 'https://bmclapi2.bangbang93.com/',
                        'https://files.minecraftforge.net/maven/': 'https://bmclapi2.bangbang93.com/maven/',
                        'https://libraries.minecraft.net/': 'https://bmclapi2.bangbang93.com/maven/'}

        self.mcbbsapi = {}
        for key, value in self.bmclapi.items():
            self.mcbbsapi[key] = value.replace('https://bmclapi2.bangbang93.com', 'https://download.mcbbs.net')

        self.mojangapi = {'https://launchermeta.mojang.com/': 'https://launchermeta.mojang.com/',
                          'https://launcher.mojang.com/': 'https://launcher.mojang.com/',
                          'https://files.minecraftforge.net/maven/': 'https://files.minecraftforge.net/maven/',
                          'https://libraries.minecraft.net/': 'https://libraries.minecraft.net/'}

        self.api = self.mojangapi

    def get_versions_list(self) -> json:
        url = self.api['https://launchermeta.mojang.com/'] + 'mc/game/version_manifest.json'
        data = hpsl.Network.web_request(url)

        return json.loads(data)

    def get_version_json(self, ver: str) -> json:

        return json.loads(self.get_version_json_text(ver))

    def get_version_json_text(self, ver: str) -> str:
        url = ''
        for i in self.get_versions_list()['versions']:
            if i['id'] == ver:
                url = i['url'].replace('https://launchermeta.mojang.com/', self.api['https://launchermeta.mojang.com/'])
        try:
            data = hpsl.Network.web_request(url)
        except BaseException as err:
            raise err

        return data

    def get_game_files_list(self, file_json: json) -> list:
        return_list = []
        # get lib
        for lib_json in file_json['libraries']:
            if 'artifact' in lib_json['downloads']:
                download_parameters = lib_json['downloads']['artifact']
                path = str(download_parameters['path'])
                sha1 = str(download_parameters['sha1'])
                url = str(download_parameters['url']).replace(
                    'https://libraries.minecraft.net/', self.api[
                        'https://libraries.minecraft.net/'])
                size = str(download_parameters['size'])
                return_list.append([path, size, sha1, url, 'lib'])
            if 'classifiers' in lib_json:

                if sys.platform.startswith('linux'):
                    # linux
                    download_type = 'natives-linux'

                elif sys.platform.startswith('darwin'):
                    # mac os
                    download_type = 'natives-osx'

                elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                    # win
                    if 'natives-windows' in lib_json['downloads']['classifiers']:
                        download_type = 'natives-windows'
                    elif platform.architecture()[0] == '64bit':
                        download_type = 'natives-windows-64'
                    elif platform.architecture()[0] == '32bit':
                        download_type = 'natives-windows-32'
                    else:
                        download_type = ''

                else:
                    download_type = ''

                download_parameters = lib_json['classifiers'][download_type]
                path = str(download_parameters['path'])
                sha1 = str(download_parameters['sha1'])
                url = str(download_parameters['url']).replace(
                    'https://libraries.minecraft.net/', self.api[
                        'https://libraries.minecraft.net/'])
                size = str(download_parameters['size'])
                return_list.append([path, size, sha1, url, 'lib'])

        # get main file
        download_parameters = file_json['downloads']['client']
        path = ''
        sha1 = str(download_parameters['sha1'])
        url = str(download_parameters['url']).replace(
            'https://launcher.mojang.com/', self.api[
                'https://launcher.mojang.com/'])
        size = str(download_parameters['size'])
        return_list.append([path, size, sha1, url, 'lib'])

        return return_list

    def complete_files(self, file_json: json, minecraft_dir: str):
        save_path = ''
        for download_parameters in self.get_game_files_list(file_json):
            if download_parameters[4] == 'lib':
                try:
                    self.__download_lib_file(minecraft_dir, download_parameters[0], save_path, download_parameters[3],
                                             download_parameters[2])
                except BaseException as err:
                    raise err

    @staticmethod
    def __download_lib_file(minecraft_dir, path, save_path, url, sha1):
        save_path = os.path.join(save_path, minecraft_dir, 'libraries')
        for path_fragment in path.split('/'):
            save_path = os.path.join(save_path, path_fragment)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        if not os.path.exists(save_path):
            hpsl.Network.download(url, save_path)
            if os.path.exists(save_path):
                i = 0
                while hashlib.sha1(open(save_path, 'rb').read()).hexdigest() != sha1:
                    i += 1
                    print('The downloaded file sha1 does not match')
                    hpsl.Network.download(url, save_path)
                    if i > 3:
                        break

    @staticmethod
    def download_client(file_json: json, minecraft_dir: str, name: str):
        try:
            save_path = os.path.join(minecraft_dir, 'versions', name, '{}.jar'.format(name))

            hpsl.Network.download(file_json['downloads']['client']['url'], save_path)
        except BaseException as err:
            raise err

    @staticmethod
    def download_server(file_json: json, save_path: str, name: str):
        try:
            hpsl.Network.download(file_json['downloads']['server']['url'], save_path)
        except BaseException as err:
            raise err
