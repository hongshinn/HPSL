import os
import platform
import sys

import hpsl.GameFile
from hpsl import Util
from hpsl import LauncherInformation


class Launch:
    def __init__(self):
        self.class_client = hpsl.GameFile.Client()
        self.class_download = hpsl.GameFile.Download()

    def launch(self, ver: str, minecraft_dir: str, java_path: str, jvm: str, player_name: str, uuid: str,
               access_token: str,
               extra_parameters: str,
               xmn='256m', xmx='1024m', height=480, width=854, version_isolation=False, version_type=''):

        os.popen(self.get_launch_script(ver, minecraft_dir, java_path, jvm, player_name, uuid,
                                        access_token,
                                        extra_parameters, xmn, xmx, height, width, version_isolation, version_type))

    def get_launch_script(self, ver: str, minecraft_dir: str, java_path: str, jvm: str, player_name: str, uuid: str,
                          access_token: str,
                          extra_parameters: str,
                          xmn='256m', xmx='1024m', height=480, width=854, version_isolation=False,
                          version_type='') -> str:
        if version_type == '':
            version_type = '{}-{}'.format(LauncherInformation.launcher_name, LauncherInformation.launcher_version)
        client_json = self.class_client.get_client_json(ver, minecraft_dir)
        if client_json['minimumLauncherVersion'] <= 18:
            return self.get_launch_script_18(access_token, extra_parameters, height, java_path, jvm,
                                             minecraft_dir,
                                             player_name, uuid, ver, version_isolation, version_type, width, xmn,
                                             xmx)
        elif client_json['minimumLauncherVersion'] > 18:
            return self.get_launch_script_19(access_token, extra_parameters, height, java_path, jvm,
                                             minecraft_dir,
                                             player_name, uuid, ver, version_isolation, version_type, width, xmn,
                                             xmx)

    def get_launch_script_19(self, access_token, extra_parameters, height, java_path, jvm, minecraft_dir,
                             player_name,
                             uuid, ver, version_isolation, version_type, width, xmn, xmx) -> str:

        # get client json
        client_json = self.class_client.get_client_json(ver, minecraft_dir)

        # get classpath
        classpath = self.get_classpath(minecraft_dir, ver, client_json)

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

    def get_launch_script_18(self, access_token, extra_parameters, height, java_path, jvm, minecraft_dir,
                             player_name,
                             uuid, ver, version_isolation, version_type, width, xmn, xmx) -> str:
        # set extra parameters
        extra_parameters += '--height {} --width {}'.format(str(height), str(width))

        # set jvm
        jvm += '-Dlog4j2.formatMsgNoLookups=true ' \
               '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump ' \
               '-Xmn{} -Xmx{}'.format(xmn, xmx)

        # get client json
        client_json = self.class_client.get_client_json(ver, minecraft_dir)

        # get classpath
        classpath = '-cp "' + self.get_classpath(minecraft_dir, ver, client_json) + '"'

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
        client_json = self.class_client.get_client_json(ver, mc_dir)

        for lib_json in client_json['libraries']:
            download_type = ''
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

    def get_classpath(self, minecraft_dir, ver, client_json):

        classpath = ''
        for file in self.class_download.get_client_files_list(client_json):
            if file[4] == 'lib' and file[0] != '':
                classpath += Util.path_conversion(os.path.join(minecraft_dir, 'libraries'), file[0]) + ';'

        classpath = classpath + os.path.join(minecraft_dir, 'versions', ver, '{}.jar'.format(ver)) + ''
        return classpath
