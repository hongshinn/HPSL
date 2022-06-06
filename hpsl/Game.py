import hpsl.GameFile


class Launch:
    def __init__(self):
        self.class_client = hpsl.GameFile.Client()
        self.class_download = hpsl.GameFile.Download()

    def launch(self, ver: str, minecraft_dir: str):
        client_json = self.class_client.get_client_json(ver, minecraft_dir)
        self.class_download.get_client_files_list(client_json)