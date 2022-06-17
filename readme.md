# HPSL
## 介绍
HPSL是一个未完工的python的minecraft启动器,当然你也可以当成一个高兼容性的启动模块

本启动器不依赖于任何第三方库

已测试过的python版本=['3.8.4', '3.11.0b3']
## 计划
- [x] 文件补全
- [x] 纯净端启动
- [x] 高版本启动
- [x] 多线程下载
- [ ] java下载
- [x] java自动扫描
- [ ] UI
- [ ] 铁砧,布料,鸡蛋,高清的支持
- [ ] 修改窗口标题
## 使用
获取版本列表:
~~~ python
import hpsl.GameFile
pt = hpsl.GameFile.Download()
pt.get_versions_list_online()
~~~

安装版本+补全文件:
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

补全文件
~~~ python
import hpsl.GameFile
mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
mc_ver = mc_dir.get_client('1.19')
mc_ver.complete_files()
~~~

启动游戏
~~~ python
import hpsl.GameFile
java_path = 'E:\\jdk-17\\jdk-17_windows-x64_bin\\jdk-17.0.2\\bin\\java.exe'
mc_dir = hpsl.GameFile.MinecraftDir('F:\\.minecraft')
mc_ver = mc_dir.get_client('1.19')
mc_ver.launch(java_path, '', ('hsn', '0', '0'), '')
~~~

单次实现下载,补全,启动实例
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