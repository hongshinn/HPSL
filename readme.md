# HPSL
## 介绍
HPSL是一个未完工的python的minecraft启动器

本启动器不依赖于任何第三方库
## 计划
- [x] 文件补全
- [x] 纯净端启动
- [x] 高版本启动
- [x] 多线程下载
- [ ] java下载
- [ ] UI
- [ ] 铁砧,布料,鸡蛋,高清的支持
- [ ] 修改窗口标题
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
import hpsl.GameFile
lc = hpsl.GameFile.Launch()
lc.launch('1.8.9a', 'E:\\.minecraft', 'E:\\jdk1.8.0_261\\bin\\java.exe', '',
                'hsn', '0', '0', '', '256m', '1024m')
~~~