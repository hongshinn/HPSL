# HPSL
## 介绍
HPSL是一个未完工的python的minecraft启动模块
不过现在应该只能启动1.6以上,1.12以下
## 使用
获取版本列表:
~~~ python
import hpsl.GameFile
pt = hpsl.GameFile.Download()
pt.get_versions_list()
~~~

获取客户端json(网络):
~~~ python
import hpsl.GameFile
pt = hpsl.GameFile.Download()
json = pt.get_client_json('1.8')
~~~

补全文件
~~~ python
import hpsl.GameFile
pt = hpsl.GameFile.Download()
json = pt.get_client_json('1.8') 
pt.complete_files(json, 'F:\\.minecraft')
~~~

启动游戏
~~~ python
import hpsl.Game
lc = hpsl.GameFile.Launch()
lc.launch('1.8.9a', 'E:\\.minecraft', 'E:\\jdk1.8.0_261\\bin\\java.exe', '',
                'hsn', '0', '0', '', '256m', '1024m')
~~~