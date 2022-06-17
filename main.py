import hpsl.GameFile

if __name__ == '__main__':
    java_path = 'E:\\jdk-17\\jdk-17_windows-x64_bin\\jdk-17.0.2\\bin\\java.exe'
    mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
    if mc_dir.is_client_exists('1.19'):
        mc_ver = mc_dir.get_client('1.19')
    else:
        mc_ver = mc_dir.create_client('1.19')
    if not mc_ver.is_client_json_exists():
        mc_ver.set_client_json_online('1.19')
    mc_ver.complete_files()
    mc_ver.launch(java_path, '', ('hsn', '0', '0'), '')

