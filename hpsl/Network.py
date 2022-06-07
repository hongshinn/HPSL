import threading
import urllib.request
import ssl


class DownloadThread(threading.Thread):
    def __init__(self, url, path, semaphore):
        threading.Thread.__init__(self)
        self.path = path
        self.url = url
        self.semaphore = semaphore

    def run(self):
        self.semaphore.acquire()
        urllib.request.urlretrieve(self.url, self.path)
        self.semaphore.release()


def web_request(url):
    req = urllib.request.Request(url, unverifiable=True)
    resp = urllib.request.urlopen(req)
    data = resp.read().decode('utf-8')
    return data


def download(url, path, multithreading=True, max_threads=64):
    if multithreading:
        semaphore = threading.BoundedSemaphore(max_threads)
        download_thread = DownloadThread(url, path, semaphore)
        download_thread.start()
    else:
        try:
            urllib.request.urlretrieve(url, path)
        except Exception as err:
            print(err)
