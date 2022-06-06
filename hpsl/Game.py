import os

import hpsl.GameFile
from hpsl import Util


class Launch:
    def __init__(self):
        self.class_client = hpsl.GameFile.Client()
        self.class_download = hpsl.GameFile.Download()

    def launch(self, ver: str, minecraft_dir: str):
        # get client json
        client_json = self.class_client.get_client_json(ver, minecraft_dir)

        # get classpath
        classpath = self.get_classpath(minecraft_dir, ver, client_json)

        # get main class
        main_class = client_json['mainClass']

        #
        print(classpath)

    def get_classpath(self, minecraft_dir, ver, client_json):

        classpath = '"'
        for file in self.class_download.get_client_files_list(client_json):
            if file[4] == 'lib' and file[0] != '':
                classpath += Util.path_conversion(os.path.join(minecraft_dir, 'libraries'), file[0]) + ';'
        classpath = classpath[:-1] + '"'
        return classpath
