# HPSL
## 介绍
HPSL是一个未完工的python的minecraft启动模块
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
