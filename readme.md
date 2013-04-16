## Build Yourown Project

一个实时的自定义在线打包服务，内部使用。

## Project details

0. 为纪念[冰火第三季](http://zh.asoiaf.wikia.com/wiki/%E5%86%B0%E4%B8%8E%E7%81%AB%E4%B9%8B%E6%AD%8C%E4%B8%AD%E6%96%87%E7%BB%B4%E5%9F%BA)开播，以及更好的把精力投入到公共库的工作。

1. 支持极光和X光两个项目的各种打包需求。未来可以很容易的扩展，比如增加其他项目、更改操作系统平台、版本构建工具和版本控制方式等。

2. client端基于[realtime web](https://en.wikipedia.org/wiki/Real-time_web)，可实时同步编译机状态，用户界面UI基于[bootstrap](http://twitter.github.io/bootstrap/)和[jquery](http://jquery.com/)。支持chrome、safari等严格实现标准的浏览器（内网访问[http://192.168.10.62:13412/](http://192.168.10.68:13412/)），支持firefox开发版、ios safari，推荐用chrome浏览，或以chrome插件形式使用。

3. server端基于[python tornado](http://www.tornadoweb.org/)框架，异步高并发，支持多用户，多台编译机同时部署。

4. worker端支持单机多份和多机方式部署，纯python编写，同时支持offline模式下的手动命令行方式工作。由于SVN集中式代码提交的局限性，目前仅提供一个worker。

5. client端chrome插件提供更新机制，server端支持热更新，server和worker端都支持挂起自动重连，理论上可保持7X24小时不当机。

6. 为方便开发，代码托管在[bitbucket](https://bitbucket.org/xfork)上：
	```
	$ git clone https://bitbucket.org/xfork/byp.git
	```
7. 图片资源、have a rest 中的小游戏基于网络。 

##
# Have fun!
