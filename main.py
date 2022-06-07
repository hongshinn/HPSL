import hpsl.GameFile
import hpsl.Game
import os

if __name__ == '__main__':
    pt = hpsl.GameFile.Download()
    pt.api = pt.mojangapi
    lc = hpsl.Game.Launch()
    cf = hpsl.GameFile.Client()
    if cf.is_client_json_exist('1.8.9a', 'E:\\.minecraft'):
        json = cf.get_client_json('1.8.9a', 'E:\\.minecraft')
    else:
        print('Getting json')
        json = pt.get_client_json('1.8.9a')
        print('Saving json')
        cf.save_client_json('1.8.9a', 'E:\\.minecraft', json)
    # print(pt.get_game_files_list(json))
    print('Completing files')
    pt.complete_files(json, 'E:\\.minecraft')

    # pt.download_client(json, 'F:\\.minecraft', '1.8')
    print('launching')
    print(lc.launch('1.8.9a', 'E:\\.minecraft', 'E:\\jdk1.8.0_261\\bin\\java.exe', '',
                    'hsn', '0', '0', '', '256m', '1024m'))
