import hpsl.GameFile
import hpsl.Game

if __name__ == '__main__':
    pt = hpsl.GameFile.Download()
    pt.api = pt.mcbbsapi
    lc = hpsl.Game.Launch()
    cf = hpsl.GameFile.Client()

    mc_dir = 'F:\\.minecraft'
    ver = '1.12.2'
    java_path = 'E:\\jdk1.8.0_261\\bin\\java.exe'

    if cf.is_client_json_exist(ver, mc_dir):
        json = cf.get_client_json(ver, mc_dir)
    else:
        print('Getting json')
        json = pt.get_client_json_online(ver)
        print('Saving json')
        cf.save_client_json(ver, mc_dir, json)

    print('Completing files')
    pt.complete_files(json, mc_dir)
    print('Download client')
    pt.download_client(ver, mc_dir)

    print('Launching')
    print(lc.launch(ver, mc_dir, java_path, '',
                    'hsn', '0', '0', '', '256m', '1024m', version_isolation=True))
