import hpsl.GameFile
import os

if __name__ == '__main__':
    pt = hpsl.GameFile.Download()
    pt.api = pt.mojangapi
    cf = hpsl.GameFile.Client()
    if cf.is_client_json_exist('1.8', 'F:\\.minecraft'):
        json = cf.get_client_json('1.8', 'F:\\.minecraft')
    else:
        print('Getting json')
        json = pt.get_client_json('1.8')
        print('Saving json')
        cf.save_client_json('1.8', 'F:\\.minecraft', json)
    # print(pt.get_game_files_list(json))
    print('Completing files')
    pt.complete_files(json, 'F:\\.minecraft')
    pt.download_client(json, 'F:\\.minecraft', '1.8')
