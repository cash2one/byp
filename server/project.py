# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	project configuration
    
@brief
    
"""


#sln名称，介绍，负责人，分类，被哪些工程依赖
bdkv_slns = [
	['commonlib','公共lib库','刘恒','base',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle',[]],
	['logicmisc','产品中间层组件','杨彦召','middle',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','middle',[]],
	['client','产品中间层组件','杨彦召','middle',[]],
	['commondll','公共dll库','刘恒','base',[]],
	['avcommon','杀毒公共模块','务孟庆','module',[]],
	['filemon','文件监控模块','武广柱','module',[]],
	['avhips','主动防御模块','曹杨','module',[]],
	['drivermanager','驱动管理模块','曹杨','module',[]],
	['sysrepair','系统修复模块','周吉文','module',[]],
	['antivirus','杀毒模块','赵欣','module',[]],
	['bdkv','杀毒主程序模块','易善鸿','module',[]],
	['bd0001','驱动模块','曹杨','module',[]],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','base',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle',[]],
	['logicmisc','产品中间层组件','杨彦召','middle',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','middle',[]],
	['client','产品中间层组件','杨彦召','middle',[]],
	['commondll','公共dll库','刘恒','base',[]],
	['bdnd','bdnd是什么','王超','module',[]],
	['syscleaner','系统清理模块','张巍','module',[]],
	['sysaccelerator','系统加速模块','赫卫卿','module',[]],
	['soacceleratorplugin','软件优化加速插件','赫卫卿','module',[]],
	['socleanerplugin','系统优化清理插件','张巍','module',[]],
	['somanager','软件优化管家','张凯','module',[]],
	['soshortcutplugin','软件优化快捷插件','张凯','module',[]],
	['swmanager','软件管理模块','张凯','module',[]],
	['qmlib','qmlib是什么','张巍','middle',[]],
	['qmgarbagecleaner','垃圾清理模块','张巍','module',[]],
	['homepageplugins','主页插件','杨彦召','module',[]],
	['mainframeplugins','框架插件','杨彦召','module',[]],
	['main','极光主程序','杨彦召','module',[]],
]

projects = {
	'X光':bdkv_slns,
	'极光':bdm_slns,
}

#选项名称，check还是radio，阶段，显示名称，tooltip名称，对应的值
bdkv_options = {
	#'prebuild':['check','before','清理','打包前的清理工作'],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','3','default'),('checkout','所有相关工程从代码服务器重新签出','4')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','1','default'),('rebuild','完全重新编译','2')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','1','default')]],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2','default'),('all','全部进行编译','3')]],

	'pack':['check','build','打包资源','重新打包资源'],
	#'signdriver':['check','build','驱动签名','更新驱动签名'],
	#'signkav':['check','build','卡巴签名','更新卡巴签名'],
	#'signbaidu':['check','build','百度签名','更新百度签名'],
	
	'sign':['check','build','生成文件签名','对打包生成的文件进行签名'],
	'install':['check','build','生成安装包','生成安装包'],

	#'send':['radio','after',[('Ignore','生成的安装包不发送往任何地方','0'),('安装包归档','生成的安装包发送至归档目录',1,'default'),('mailme','生成安装包后给我发邮件',2)]],
	'send':['check','after','安装包归档','生成的安装包发送至归档目录'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录'],
	#'postbuild':['check','after','清理','打包后的清理工作'],
}

bdm_options = {
	'prebuild':['check','before','清理','打包前的清理工作'],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','4','default'),('checkout','所有相关工程从代码服务器重新签出','3')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','1','default'),('rebuild','完全重新编译','2')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','1','default')]],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2','default'),('all','全部进行编译','3')]],
	
	'pack':['check','build','打包资源','重新打包资源'],
	#'sign':['check','build','百度签名','更新百度签名'],
	
	'sign':['check','build','生成文件签名','对打包生成的文件进行签名'],
	'install':['check','build','生成安装包','生成安装包'],

	#'send':['radio','after',[('Ignore','生成的安装包不发送往任何地方','0'),('安装包归档','生成的安装包发送至归档目录',1,'default'),('mailme','生成安装包后给我发邮件',2)]],
	'send':['check','after','安装包归档','生成的安装包发送至归档目录'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录'],
	'postbuild':['check','after','清理','打包后的清理工作'],
}

build_options = {
	'X光': bdkv_options,
	'极光': bdm_options,
}

#支持的代码基依赖
svn_codebase = [('Branch','基于特定分支构造',1),('Tag','基于特定Tag构造',2),('Trunk','基于主线构造',3,'default'),('Revision','基于特定Revision构造',4)]

build_depends = {
	'X光': svn_codebase,
	'极光': svn_codebase,
}
