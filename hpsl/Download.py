import json
import hpsl.web


class Download:
    def __init__(self):
        self.api = 'https://bmclapi2.bangbang93.com/'

    def get_versions_list(self):
        url = self.api + 'mc/game/version_manifest.json'
        data = hpsl.web.web_request(url)

        return json.dumps(data)

    def get_version_json(self, ver):

        return json.dumps(self.get_version_json_text(ver))

    def get_version_json_text(self, ver):
        url = self.api + '/version/' + ver + '/json'
        try:
            data = hpsl.web.web_request(url)

        except:
            pass

        return data
