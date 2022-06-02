import urllib.request
import ssl


def web_request(url):
    req = urllib.request.Request(url, unverifiable=True)
    resp = urllib.request.urlopen(req)
    data = resp.read().decode('utf-8')
    return data


def download(url, path):
    try:
        urllib.request.urlretrieve(url, path)
    except Exception as err:
        print(err)
