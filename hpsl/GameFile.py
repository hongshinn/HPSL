import json

import hpsl.Network


class Download:
    def __init__(self):
        self.api = 'https://bmclapi2.bangbang93.com/'

    def get_versions_list(self) -> json:
        url = self.api + 'mc/game/version_manifest.json'
        data = hpsl.Network.web_request(url)

        return json.dumps(data)

    def get_version_json(self, ver: str) -> json:

        return json.dumps(self.get_version_json_text(ver))

    def get_version_json_text(self, ver: str) -> str:
        url = self.api + '/version/' + ver + '/json'

        try:
            data = hpsl.Network.web_request(url)
        finally:
            pass

        return data
