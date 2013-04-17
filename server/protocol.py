# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	协议约定
    
@brief

"""

#发送json格式化字符串，unicode编码，如u'{"msrc":"ws-client-connect",content":"hello"}'
#各字段含义为：
#
#
#			msrc [message source 消息源]
######################################################################################
#				 server和client通信用
#				 = "ws-client-connect"						client连线
#				 = "ws-project-select"						发送支持打包的产品名
#				 = "ws-sln-select"							发送该产品对应的工程列表
#				 = "ws-build-options"						发送支持的打包配置
#				 = "ws-code-base"							支持的编译依赖
#				 = "ws-cb-detail"							编译依赖细节
#				 = "ws-build-reason"						打包原因
#				 = "ws-user-email"							用户email
#				 = "ws-btn-build"							通知打包
#				 = "ws-build-progress"						打包进度更新
#				 = "ws-build-log"							主打包log窗口
#				 = "ws-worker-select"						切换worker响应
#				 = "ws-worker-status"						更新worker状态
#				 = "ws-wroker-detail"						更新worker状态细节
#				 = "ws-worker-running"						正在运行的worker更新
#				 = "ws-worker-idle"							当前idle的worker更新
#				 = "ws-worker-error"						打包出错的worker更新
#				 = "ws-query-buildlog"						client刚连上，询问当前打包状态
#				 = "ws-build-reset"							编译机开始工作
#				 = "ws-user-info"							通知客户端更新编译机使用者信息
######################################################################################
#				 server和worker通信用
#				 = "wk-heart-beat"							判断worker是否在线
#				 = "wk-start-build"							通知worker开始干活
#				 = "wk-worker-connect"						worker连线
#				 = "wk-build-log"							worker工作日志
#				 = "wk-status-change"						worker状态切换
#				 = "wk-build-progress"						打包进度更新
#				 = "wk-build-finish"						打包完成
#				 = "wk-user-info"							告知server当前worker使用者信息
#
#
#		 content
######################################################################################
#		 		 = "..."									根据具体type类型来解析
#
#
