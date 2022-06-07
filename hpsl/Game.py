import os
import platform
import sys

import hpsl.GameFile
from hpsl import Util


class Launch:
    def __init__(self):
        self.class_client = hpsl.GameFile.Client()
        self.class_download = hpsl.GameFile.Download()

    def launch(self, ver: str, minecraft_dir: str, java_path: str, jvm: str, player_name: str, uuid: str,
               access_token: str,
               extra_parameters: str,
               xmn='256m', xmx='1024m', height=480, width=854):
        os.system(self.get_launch_script(ver, minecraft_dir, java_path, jvm, player_name, uuid,
                                         access_token,
                                         extra_parameters, xmn, xmx, height, width))

    def get_launch_script(self, ver: str, minecraft_dir: str, java_path: str, jvm: str, player_name: str, uuid: str,
                          access_token: str,
                          extra_parameters: str,
                          xmn='256m', xmx='1024m', height=480, width=854) -> str:
        # set extra parameters
        extra_parameters += '--height {} --width {}'.format(str(height), str(width))
        # set jvm
        jvm += '-Dlog4j2.formatMsgNoLookups=true ' \
               '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump ' \
               '-Xmn{} -Xmx{}'.format(xmn, xmx)
        # get client json
        client_json = self.class_client.get_client_json(ver, minecraft_dir)

        # get classpath
        classpath = self.get_classpath(minecraft_dir, ver, client_json)

        # get main class
        main_class = str(client_json['mainClass'])

        # set assets
        assets_path = os.path.join(minecraft_dir, 'assets')

        # get mc arg
        minecraft_arg = str(client_json['minecraftArguments']). \
            replace('${game_directory}', minecraft_dir). \
            replace('${auth_player_name}', player_name). \
            replace('${version_name}', ver). \
            replace('${assets_root}', assets_path). \
            replace('${assets_index_name}', client_json['assetIndex']['id']). \
            replace('${auth_uuid}', uuid). \
            replace('${auth_access_token}', access_token). \
            replace('${user_properties}', '{}'). \
            replace('${user_type}', 'mojang')

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
                path = Util.path_conversion(os.path.join(mc_dir, 'libraries'), path)
                Util.un_zip(path, os.path.join(mc_dir, 'versions', ver, '{}-natives'.format(ver)))

    def get_classpath(self, minecraft_dir, ver, client_json):

        classpath = '-cp "'
        for file in self.class_download.get_client_files_list(client_json):
            if file[4] == 'lib' and file[0] != '':
                classpath += Util.path_conversion(os.path.join(minecraft_dir, 'libraries'), file[0]) + ';'

        classpath = classpath + os.path.join(minecraft_dir, 'versions', ver, '{}.jar'.format(ver)) + '"'
        return classpath
