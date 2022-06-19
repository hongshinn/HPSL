import json
import logging
import os
import platform
import re
import shutil
import sys
import threading

import hpsl.Network
from hpsl import Util, LauncherInformation


class MinecraftClient:
    def __init__(self, mc_dir: str, name: str):
        # get logger
        logging.basicConfig(filename='log.txt')
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            'MinecraftClient class initialization, minecraft directory: {}, client name: {}'.format(mc_dir, name))
        self.name = name
        self.mc_dir = mc_dir
        self.path = os.path.join(mc_dir, 'versions', name)
        self.jar_path = os.path.join(mc_dir, 'versions', name, '{}.jar'.format(name))
        self.json_path = os.path.join(mc_dir, 'versions', name, '{}.json'.format(name))

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.json = json.load(f)
        except IOError as err:
            self.logger.error(err)

        # 尽量不要用bmclapi,bmclapi的open bmclapi过不了ssl,会下载失败
        self.bmclapi = {'https://launchermeta.mojang.com/': 'https://bmclapi2.bangbang93.com/',
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

    @staticmethod
    def __download_lib_file(mc_dir, path, save_path, url) -> threading:
        save_path = os.path.join(save_path, mc_dir, 'libraries')
        save_path = Util.path_conversion(save_path, path)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        if not os.path.exists(save_path):
            t = hpsl.Network.download(url, save_path)
            return t

    def is_client_json_exists(self):
        return os.path.exists(self.json_path)

    def is_client_jar_exists(self):
        return os.path.exists(self.jar_path)

    def set_client_json(self, client_json: json):
        self.json = client_json
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(json, f)

    def set_client_json_online(self, ver: str):
        dl = Download()
        try:
            self.json = dl.get_client_json_online(ver)
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.json, f)
        except BaseException as err:
            self.logger.error(err)

    def get_client_files_list(self) -> list:
        file_json = self.json

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
                download_type = ''
                if sys.platform.startswith('linux') and 'natives-linux' in lib_json['downloads']['classifiers']:
                    # linux
                    download_type = 'natives-linux'

                elif sys.platform.startswith('darwin') and 'natives-osx' in lib_json['downloads']['classifiers']:
                    # mac os
                    download_type = 'natives-osx'

                elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                    # win

                    if 'natives-windows' in lib_json['downloads']['classifiers']:

                        download_type = 'natives-windows'
                    elif platform.architecture()[0] == '64bit':
                        if 'natives-windows-64' in lib_json['downloads']['classifiers']:
                            download_type = 'natives-windows-64'
                    elif platform.architecture()[0] == '32bit':
                        if 'natives-windows-32' in lib_json['downloads']['classifiers']:
                            download_type = 'natives-windows-32'
                    else:
                        download_type = ''

                else:
                    download_type = ''
                if download_type != '':
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

    def complete_files(self):
        mc_dir = self.mc_dir
        if not self.is_client_jar_exists():
            self.download_client()
        save_path = ''
        threading_list = []
        for download_parameters in self.get_client_files_list():
            if download_parameters[4] == 'lib' and (not os.path.exists(download_parameters[0])):
                try:
                    t = self.__download_lib_file(mc_dir, download_parameters[0], save_path, download_parameters[3])
                    threading_list.append(t)
                except BaseException as err:
                    raise err

        self.complete_assets()
        for t in threading_list:
            if t is not None:
                t.join()

    def complete_assets(self):
        threading_list = []
        mc_dir = self.mc_dir
        file_json = self.json
        save_path = os.path.join(mc_dir, 'assets')
        indexes_path = os.path.join(save_path, 'indexes', '{}.json'.format(file_json['assetIndex']['id']))

        if not os.path.exists(os.path.dirname(indexes_path)):
            os.makedirs(os.path.dirname(indexes_path))

        if not os.path.exists(indexes_path):
            hpsl.Network.download(file_json['assetIndex']['url'], indexes_path, multithreading=False)

        with open(indexes_path, 'r', encoding='utf8') as file:
            indexes_json = json.load(file)

        for file_name in indexes_json['objects']:
            if file_name != '':
                assets_hash = str(indexes_json['objects'][file_name]['hash'])
                first_two_hash = str(indexes_json['objects'][file_name]['hash'])[:2]

                if not os.path.exists(os.path.dirname(os.path.join(save_path, 'objects', first_two_hash, assets_hash))):
                    os.makedirs(os.path.dirname(os.path.join(save_path, 'objects', first_two_hash, assets_hash)))
                if not os.path.exists(os.path.join(save_path, 'objects', first_two_hash, assets_hash)):
                    t = hpsl.Network.download(
                        '{}{}/{}'.format(self.api['https://resources.download.minecraft.net/'], first_two_hash,
                                         assets_hash),
                        os.path.join(save_path, 'objects', first_two_hash, assets_hash))
                    threading_list.append(t)
        for t in threading_list:
            t.join()

    def download_client(self):
        file_json = self.json
        try:
            save_path = self.jar_path
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))
            if not os.path.exists(save_path):
                hpsl.Network.download(str(file_json['downloads']['client']['url']).replace(
                    'https://launcher.mojang.com/', self.api[
                        'https://launcher.mojang.com/']), save_path, False)

        except BaseException as err:
            raise err

    def launch(self, java_path: str, jvm: str, player_login_parameters,
               extra_parameters: str,
               xmn='256m', xmx='1024m', height=480, width=854, version_isolation=False, version_type='', lang=None):
        if lang is not None:
            if os.path.exists(os.path.join(self.mc_dir, 'options.txt')):
                with open(os.path.join(self.mc_dir, 'options.txt'), 'r+', encoding='utf-8') as f:
                    str_re = re.compile('lang:.*\n')
                    str_write = str_re.sub('lang:{}\n'.format(lang), f.read())
                    f.seek(0, 0)
                    f.write(str_write)
            else:
                with open(os.path.join(self.mc_dir, 'options.txt'), 'x', encoding='utf-8') as f:
                    f.write('lang:{}\n'.format(lang))

        os.popen(self.get_launch_script(java_path, jvm, player_login_parameters,
                                        extra_parameters, xmn, xmx, height, width, version_isolation, version_type))

    def get_launch_script(self, java_path: str, jvm: str, player_login_parameters,
                          extra_parameters: str,
                          xmn='256m', xmx='1024m', height=480, width=854, version_isolation=False,
                          version_type='') -> str:
        if version_type == '':
            version_type = '{}-{}'.format(LauncherInformation.launcher_name, LauncherInformation.launcher_version)
        client_json = self.json
        if client_json['minimumLauncherVersion'] <= 18:
            return self.get_launch_script_18(extra_parameters, height, java_path, jvm,
                                             player_login_parameters, version_isolation, version_type, width, xmn,
                                             xmx)
        elif client_json['minimumLauncherVersion'] > 18:
            return self.get_launch_script_19(extra_parameters, height, java_path, jvm,
                                             player_login_parameters, version_isolation, version_type, width, xmn,
                                             xmx)

    def get_launch_script_19(self, extra_parameters, height, java_path, jvm,
                             player_login_parameters, version_isolation, version_type, width, xmn, xmx) -> str:
        player_name, uuid, access_token = player_login_parameters
        minecraft_dir = self.mc_dir
        ver = self.name
        # get client json
        client_json = self.json

        # get classpath
        classpath = self.get_classpath()

        # get main class
        main_class = str(client_json['mainClass'])

        # set assets
        assets_path = os.path.join(minecraft_dir, 'assets')

        # get mc arg
        mc_arg_game = client_json['arguments']['game']
        arg_list = []
        can_append = False
        for arg in mc_arg_game:
            # get rules
            if 'rules' in arg:
                for rule in arg['rules']:
                    can_act = False
                    for feature in rule['features']:

                        # Judgment Rules
                        if feature == 'is_demo_user':
                            can_act = not rule['features'][feature]
                        elif feature == 'has_custom_resolution':
                            can_act = rule['features'][feature]

                    if rule['action'] == 'allow' and can_act:
                        can_append = True

                if can_append:
                    if isinstance(arg['value'], list):
                        for value in arg['value']:
                            arg_list.append('"{}"'.format(value))
                    else:
                        arg_list.append('"{}"'.format(arg['value']))
            else:
                arg_list.append('"{}"'.format(arg))
        minecraft_arg = Util.list2str(arg_list, ' ')
        minecraft_arg = str(minecraft_arg). \
            replace('${auth_player_name}', player_name). \
            replace('${version_name}', ver). \
            replace('${assets_root}', assets_path). \
            replace('${assets_index_name}', client_json['assetIndex']['id']). \
            replace('${auth_uuid}', uuid). \
            replace('${auth_access_token}', access_token). \
            replace('${user_properties}', '{}'). \
            replace('${user_type}', 'mojang'). \
            replace('${version_type}', version_type). \
            replace('${resolution_height}', str(height)). \
            replace('${resolution_width}', str(width))
        if version_isolation:
            minecraft_arg = minecraft_arg.replace('${game_directory}', os.path.join(minecraft_dir, 'versions', ver))
        else:
            minecraft_arg = minecraft_arg.replace('${game_directory}', minecraft_dir)

        # set jvm
        mc_arg_jvm = client_json['arguments']['jvm']
        arg_list = []
        can_append = False
        for arg in mc_arg_jvm:
            # get rules
            if 'rules' in arg:
                for rule in arg['rules']:
                    can_act = True
                    if 'name' in rule['os']:
                        can_act = can_act and (Util.get_sys_type() == rule['os']['name'])

                    if 'arch' in rule['os']:
                        can_act = can_act and (Util.get_sys_type() == rule['os']['arch'])

                    if 'version' in rule['os']:
                        can_act = can_act and ('^{}\\\\.'.format(platform.version()) == rule['os']['version'])

                    if rule['action'] == 'allow' and can_act:
                        can_append = True

                if can_append:
                    if isinstance(arg['value'], list):
                        for value in arg['value']:
                            arg_list.append('"{}"'.format(value))
                    else:
                        arg_list.append('"{}"'.format(arg['value']))
            else:
                arg_list.append('"{}"'.format(arg))

        jvm += ' -Dlog4j2.formatMsgNoLookups=true ' \
               '-Xmn{} -Xmx{} '.format(xmn, xmx) + Util.list2str(arg_list, ' ')
        jvm = jvm. \
            replace('${classpath}', classpath). \
            replace('${launcher_version}', LauncherInformation.launcher_version). \
            replace('${launcher_name}', LauncherInformation.launcher_name). \
            replace('${natives_directory}', os.path.join(minecraft_dir, 'versions', ver, '{}-natives'.format(ver)))

        # unzip natives
        self.unzip_natives(ver, minecraft_dir)

        return Util.list2str(['"{}"'.format(java_path), jvm, main_class, minecraft_arg,
                              extra_parameters], ' ')

    def get_launch_script_18(self, extra_parameters, height, java_path, jvm,
                             player_login_parameters, version_isolation, version_type, width, xmn, xmx) -> str:
        player_name, uuid, access_token = player_login_parameters
        minecraft_dir = self.mc_dir
        ver = self.name

        # set extra parameters
        extra_parameters += '--height {} --width {}'.format(str(height), str(width))

        # set jvm
        jvm += '-Dlog4j2.formatMsgNoLookups=true ' \
               '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump ' \
               '-Xmn{} -Xmx{}'.format(xmn, xmx)

        # get client json
        client_json = self.json

        # get classpath
        classpath = '-cp "' + self.get_classpath() + '"'

        # get main class
        main_class = str(client_json['mainClass'])

        # set assets
        assets_path = os.path.join(minecraft_dir, 'assets')

        # get mc arg
        minecraft_arg = str(client_json['minecraftArguments']). \
            replace('${auth_player_name}', player_name). \
            replace('${version_name}', ver). \
            replace('${assets_root}', assets_path). \
            replace('${assets_index_name}', client_json['assetIndex']['id']). \
            replace('${auth_uuid}', uuid). \
            replace('${auth_access_token}', access_token). \
            replace('${user_properties}', '{}'). \
            replace('${user_type}', 'mojang'). \
            replace('${version_type}', version_type)
        if version_isolation:
            minecraft_arg = minecraft_arg.replace('${game_directory}', os.path.join(minecraft_dir, 'versions', ver))
        else:
            minecraft_arg = minecraft_arg.replace('${game_directory}', minecraft_dir)

        # unzip natives
        self.unzip_natives(ver, minecraft_dir)

        # set natives path
        natives_path = os.path.join(minecraft_dir, 'versions', ver, '{}-natives'.format(ver))
        natives_parameter = '"-Djava.library.path={}"'.format(natives_path)
        return Util.list2str([java_path, jvm, natives_parameter, classpath, main_class, minecraft_arg,
                              extra_parameters], ' ')

    def unzip_natives(self, ver: str, mc_dir):
        client_json = self.json

        for lib_json in client_json['libraries']:
            download_type = ''
            if 'classifiers' in lib_json['downloads']:
                if sys.platform.startswith('linux') and 'natives-linux' in lib_json['downloads']['classifiers']:
                    # linux
                    download_type = 'natives-linux'

                elif sys.platform.startswith('darwin') and 'natives-osx' in lib_json['downloads']['classifiers']:
                    # mac os
                    download_type = 'natives-osx'

                elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                    # win
                    if 'natives-windows' in lib_json['downloads']['classifiers']:
                        download_type = 'natives-windows'
                    elif platform.architecture()[0] == '64bit':
                        if 'natives-windows-64' in lib_json['downloads']['classifiers']:
                            download_type = 'natives-windows-64'
                    elif platform.architecture()[0] == '32bit':
                        if 'natives-windows-32' in lib_json['downloads']['classifiers']:
                            download_type = 'natives-windows-32'
                    else:
                        download_type = ''

                else:
                    download_type = ''
                if download_type != '':
                    download_parameters = lib_json['downloads']['classifiers'][download_type]
                    path = str(download_parameters['path'])
                    path = Util.path_conversion(os.path.join(mc_dir, 'libraries'), path)
                    Util.un_zip(path, os.path.join(mc_dir, 'versions', ver, '{}-natives'.format(ver)))

    def get_classpath(self):
        ver = self.name
        minecraft_dir = self.mc_dir
        classpath = ''
        for file in self.get_client_files_list():
            if file[4] == 'lib' and file[0] != '':
                classpath += Util.path_conversion(os.path.join(minecraft_dir, 'libraries'), file[0]) + ';'

        classpath = classpath + os.path.join(minecraft_dir, 'versions', ver, '{}.jar'.format(ver)) + ''
        return classpath


class MinecraftDir:
    def __init__(self, path: str):
        self.path = path

    def get_client(self, name: str) -> MinecraftClient:
        return MinecraftClient(self.path, name)

    def is_client_exists(self, name: str) -> bool:
        return os.path.exists(os.path.join(self.path, 'versions', name))

    def create_client(self, name: str):
        os.makedirs(os.path.join(self.path, 'versions', name))
        return MinecraftClient(self.path, name)

    def del_client(self, name: str):
        shutil.rmtree(os.path.join(self.path, 'versions', name))

    def get_client_list(self) -> list:
        return os.listdir(os.path.join(self.path, 'versions'))


class Download:
    def __init__(self):
        # 尽量不要用bmclapi,bmclapi的open bmclapi过不了ssl,会下载失败
        self.bmclapi = {'https://launchermeta.mojang.com/': 'https://bmclapi2.bangbang93.com/',
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

    def get_forge_list_online(self) -> json:
        url = self.api['https://files.minecraftforge.net/maven/'] + 'net/minecraftforge/forge/json'
        data = hpsl.Network.web_request(url)

        return json.loads(data)

    @staticmethod
    def download_server(file_json: json, save_path: str):
        try:
            hpsl.Network.download(file_json['downloads']['server']['url'], save_path)
        except BaseException as err:
            raise err

    @staticmethod
    def scan_java_path_windows() -> list:
        java_list = []
        for i in range(65, 91):
            vol = chr(i) + ':\\'
            if os.path.isdir(vol):
                for root, file_dir, file_name in os.walk(vol):
                    for file in file_name:
                        if file == 'javaw.exe':
                            java_list.append(os.path.join(root, file))
        return java_list
