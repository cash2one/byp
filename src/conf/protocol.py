# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	协议约定
    
@brief
    protocol configuration
"""

#发送json格式化字符串，类似 unicode: {"id":"ws-project-select","type":"1",content":"hello","_xsrf":"1dd6c86a4f9a461aaafd01c014ae387f"}
#各字段含义为：
#
#
#			msrc [message source 消息源]
######################################################################################
#				 server和client通信用
#				 = "ws-client-connect"
#				 = "ws-project-select"						发送支持打包的产品名
#				 = "ws-sln-select"							发送该产品对应的工程列表
#				 = "ws-build-options"						发送支持的打包配置
#				 = "ws-code-base"							
#				 = "ws-cb-detail"							
#				 = "ws-build-reason"						
#				 = "ws-user-email"							
#				 = "ws-btn-build"
#				 = "ws-build-progress"
#				 = "ws-build-progress-text"
#				 = "ws-build-log"
#				 = "ws-worker-select"
#				 = "ws-worker-status"
#				 = "ws-wroker-detail"
#				 = "ws-worker-running"
#				 = "ws-worker-idle"
#				 = "ws-worker-error"
######################################################################################
#				 server和worker通信用
#				 = "wk-heart-beat"							判断worker是否在线
#				 = "wk-start-build"							通知worker开始干活
#				 = "wk-worker-connect"						worker连线
#				 = "wk-build-log"							worker工作日志
#				 = "wk-status-change"						worker状态切换
#
#			 sid [sender id 消息发送者id uuid格式]
######################################################################################
#				 = "92ecde39-62d3-44b9-8d48-b23f5053cbf6"
#
#		 content
######################################################################################
#		 		 = "..."									根据具体type类型来解析
#
#
#
#
#