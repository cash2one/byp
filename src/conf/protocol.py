# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	协议约定
    
@brief
    protocol configuration
"""

#发送json格式化字符串，类似 unicode: {"type":"info",content":"hello","_xsrf":"1dd6c86a4f9a461aaafd01c014ae387f"}
#各字段含义为：
#
#			type = "project"			发送支持打包的产品名
#				 = "sln"				发送该产品对应的工程列表
#				 = "option"				发送支持的打包配置
#				 = "progress"			发送进度更新
#				 = "log"				发送最常规，可无视的log信息
#				 = "info"				发送用户可能感兴趣的，比较重要的更新信息
#				 = "error"				打包出现错误通知用户
#
#		 content = "..."				根据具体type类型来解析
#
#
#
#
#
#
#
#
#