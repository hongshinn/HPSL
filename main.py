import hpsl.GameFile


if __name__ == '__main__':
    pt = hpsl.GameFile.Download()
    pt.api = pt.bmclapi
    print('Getting json')
    json = pt.get_version_json('1.8')
    print('Parsing')
    print(pt.get_game_files_list(json))


