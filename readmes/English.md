# HPSL

[简体中文](https://github.com/hongshinn/HPSL/blob/master/readme.md)
|
[English(current)](https://github.com/hongshinn/HPSL/blob/master/readmes/Englishi.md)

Translation provided by Google Translate
## introduce
HPSL is an unfinished python minecraft launcher, of course you can also use it as a high compatibility launch module

This launcher does not depend on any third party library

Tested python version=['3.8.4', '3.11.0b3']
## plan
- [x] file completion
- [x] vanilla client launch
- [x] high version launch
- [x] Multithreaded download
- [ ] java download
- [x] java auto scan
- [ ] UI
- [ ] Forge,Fabric,LiteLoader,Optifine
- [ ] Modify window title
## usage
Get a list of versions:
~~~ python
import hpsl.GameFile
pt = hpsl.GameFile.Download()
pt.get_versions_list_online()
~~~

Install version + completion file:
~~~ python
import hpsl.GameFile
mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
if mc_dir.is_client_exists('1.19'):
    mc_ver = mc_dir.get_client('1.19')
else:
    mc_ver = mc_dir.create_client('1.19')
if not mc_ver.is_client_json_exists():
    mc_ver.set_client_json_online('1.19')
mc_ver.complete_files()

~~~

Completion file
~~~ python
import hpsl.GameFile
mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
mc_ver = mc_dir.get_client('1.19')
mc_ver.complete_files()
~~~

start the game
~~~ python
import hpsl.GameFile
java_path = 'E:\\jdk-17\\jdk-17_windows-x64_bin\\jdk-17.0.2\\bin\\java.exe'
mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
mc_ver = mc_dir.get_client('1.19')
mc_ver.launch(java_path, '', ('hsn', '0', '0'), '')
~~~

Download, complete, and start an instance at a time
~~~ python
import hpsl.GameFile
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
~~~