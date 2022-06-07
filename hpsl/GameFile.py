import hashlib
import json
import os
import platform
import sys

import hpsl.Network
from hpsl import Util


class Download:

    def __init__(self):
        self.bmclapi = {'http://launchermeta.mojang.com/': 'https://bmclapi2.bangbang93.com/',
                        'https://launcher.mojang.com/': 'https://bmclapi2.bangbang93.com/',
                        'https://files.minecraftforge.net/maven/': 'https://bmclapi2.bangbang93.com/maven/',
                        'https://libraries.minecraft.net/': 'https://bmclapi2.bangbang93.com/maven/',
                        'https://resources.download.minecraft.net/': 'https://bmclapi2.bangbang93.com/assets/'}

        self.mcbbsapi = {}
        for key, value in self.bmclapi.items():
            self.mcbbsapi[key] = value.replace('https://bmclapi2.bangbang93.com', 'https://download.mcbbs.net')

        self.mojangapi = {'https://launchermeta.mojang.com/': 'https://launchermeta.mojang.com/',
                          'https://launcher.mojang.com/': 'https://launcher.mojang.com/',
                          'https://files.minecraftforge.net/maven/': 'https://files.minecraftforge.net/maven/',
                          'https://libraries.minecraft.net/': 'https://libraries.minecraft.net/',
                          'https://resources.download.minecraft.net/': 'https://resources.download.minecraft.net/'}

        self.api = self.mojangapi

    def get_versions_list_online(self) -> json:
        url = self.api['https://launchermeta.mojang.com/'] + 'mc/game/version_manifest.json'
        data = hpsl.Network.web_request(url)

        return json.loads(data)

    def get_client_json_online(self, ver: str) -> json:

        return json.loads(self.get_client_json_text_online(ver))

    def get_client_json_text_online(self, ver: str) -> str:
        url = ''
        for i in self.get_versions_list_online()['versions']:
            if i['id'] == ver:
                url = i['url'].replace('https://launchermeta.mojang.com/', self.api['https://launchermeta.mojang.com/'])
        try:
            data = hpsl.Network.web_request(url)
        except BaseException as err:
            raise err

        return data

    def complete_files(self, file_json: json, mc_dir: str):
        save_path = ''

        for download_parameters in self.get_client_files_list(file_json):
            if download_parameters[4] == 'lib' and (not os.path.exists(download_parameters[0])):
                try:
                    self.__download_lib_file(mc_dir, download_parameters[0], save_path, download_parameters[3],
                                             download_parameters[2])
                except BaseException as err:
                    raise err
        self.complete_assets(file_json, mc_dir)

    def complete_assets(self, file_json: json, mc_dir: str):
        save_path = os.path.join(mc_dir, 'assets')
        indexes_path = os.path.join(save_path, 'indexes', '{}.json'.format(file_json['assetIndex']['id']))

        if not os.path.exists(os.path.dirname(indexes_path)):
            os.makedirs(os.path.dirname(indexes_path))

        if not os.path.exists(indexes_path):
            hpsl.Network.download(file_json['assetIndex']['url'], indexes_path)

        with open(indexes_path, 'r', encoding='utf8') as file:
            indexes_json = json.load(file)

        for file_name in indexes_json['objects']:
            if file_name != '':
                assets_hash = str(indexes_json['objects'][file_name]['hash'])
                first_two_hash = str(indexes_json['objects'][file_name]['hash'])[:2]

                if not os.path.exists(os.path.dirname(os.path.join(save_path, 'objects', first_two_hash, assets_hash))):
                    os.makedirs(os.path.dirname(os.path.join(save_path, 'objects', first_two_hash, assets_hash)))
                if not os.path.exists(os.path.join(save_path, 'objects', first_two_hash, assets_hash)):
                    hpsl.Network.download(
                        '{}{}/{}'.format(self.api['https://resources.download.minecraft.net/'], first_two_hash,
                                         assets_hash),
                        os.path.join(save_path, 'objects', first_two_hash, assets_hash))

    def get_client_files_list(self, file_json: json) -> list:
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
            if 'classifiers' in lib_json['downloads']:

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

                download_parameters = lib_json['downloads']['classifiers'][download_type]
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

    @staticmethod
    def __download_lib_file(mc_dir, path, save_path, url, sha1):
        save_path = os.path.join(save_path, mc_dir, 'libraries')
        save_path = Util.path_conversion(save_path, path)
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

    def download_client(self, name: str, minecraft_dir: str):
        file_json = Client.get_client_json(name, minecraft_dir)
        try:
            save_path = os.path.join(minecraft_dir, 'versions', name, '{}.jar'.format(name))
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))
            if not os.path.exists(save_path):
                hpsl.Network.download(str(file_json['downloads']['client']['url']).replace(
                    'https://launcher.mojang.com/', self.api[
                        'https://launcher.mojang.com/']), save_path)
                if os.path.exists(save_path):
                    i = 0
                    while hashlib.sha1(open(save_path, 'rb').read()).hexdigest() != str(file_json['downloads'][
                                                                                            'client']['sha1']):
                        i += 1
                        print('The downloaded file sha1 does not match')

                        hpsl.Network.download(str(file_json['downloads']['client']['url']).replace(
                            'https://launcher.mojang.com/', self.api[
                                'https://launcher.mojang.com/']), save_path)
                        if i > 3:
                            break

        except BaseException as err:
            raise err

    @staticmethod
    def download_server(file_json: json, save_path: str, name: str):
        try:
            hpsl.Network.download(file_json['downloads']['server']['url'], save_path)
        except BaseException as err:
            raise err


class Client:
    @staticmethod
    def get_client_json(ver: str, mc_dir: str) -> json:
        path = os.path.join(mc_dir, 'versions', ver, '{}.json'.format(ver))
        return json.load(open(path, 'r', encoding='utf-8'))

    @staticmethod
    def save_client_json(name: str, mc_dir: str, client_json: json):
        path = os.path.join(mc_dir, 'versions', name, '{}.json'.format(name))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        open(path, 'w', encoding='utf8').write(json.dumps(client_json))

    @staticmethod
    def is_client_json_exist(name: str, mc_dir: str):
        path = os.path.join(mc_dir, 'versions', name, '{}.json'.format(name))
        return os.path.exists(path)
