import json
import os
import hpsl.Network
import sys
import platform

class Download:
    def __init__(self):
        self.api = 'https://bmclapi2.bangbang93.com/'
        # 艹,为什么bmclapi那么奇怪阿,而且还ssl错误,无语死了
        self.lib_api = 'https://libraries.minecraft.net/'

    def get_versions_list(self) -> json:
        url = self.api + 'mc/game/version_manifest.json'
        data = hpsl.Network.web_request(url)

        return json.loads(data)

    def get_version_json(self, ver: str) -> json:

        return json.loads(self.get_version_json_text(ver))

    def get_version_json_text(self, ver: str) -> str:
        url = self.api + '/version/' + ver + '/json'

        try:
            data = hpsl.Network.web_request(url)
        finally:
            pass

        return data

    def complete_files(self, file_json: json, minecraft_dir: str):
        save_path = ''
        for lib_json in file_json['libraries']:
            if 'artifact' in lib_json['downloads']:
                download_parameters = lib_json['downloads']['artifact']
                path = str(download_parameters['path'])
                sha1 = str(download_parameters['size'])
                url = str(download_parameters['url']).replace('https://libraries.minecraft.net/', self.lib_api)
                try:
                    self.__download_lib_file(minecraft_dir, path, save_path, url)

                except BaseException as err:
                    raise err
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
                sha1 = str(download_parameters['size'])
                url = str(download_parameters['url']).replace('https://libraries.minecraft.net/', self.lib_api)

    def __download_lib_file(self, minecraft_dir, path, save_path, url):
        save_path = os.path.join(save_path, minecraft_dir, 'libraries')
        for path_fragment in path.split('/'):
            save_path = os.path.join(save_path, path_fragment)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        if not os.path.exists(save_path):
            hpsl.Network.download(url, save_path)

    def download_client(self, file_json: json, minecraft_dir: str, name: str):
        try:
            save_path = os.path.join(minecraft_dir, 'versions', name, '{}.jar'.format(name))

            hpsl.Network.download(file_json['downloads']['client']['url'], save_path)
        except BaseException as err:
            raise err

