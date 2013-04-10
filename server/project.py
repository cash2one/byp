# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	工程配置信息
    
@brief
    project configuration
"""

#总的工程根目录
sln_root = '../../'

#sln名称，介绍，负责人，分类，目录，被哪些工程依赖
bdkv_slns = [
	['commonlib','公共lib库','刘恒','base','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','middle','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','middle','client_proj',[]],
	['client','产品中间层组件','杨彦召','middle','client_proj',[]],
	['commondll','公共dll库','刘恒','base','common_proj',[]],
	['avcommon','杀毒公共模块','务孟庆','module','avcommon_proj',[]],
	['filemon','文件监控','武广柱','module','avfilemon_proj',[]],
	['avhips','主动防御','曹杨','module','avhips_proj',[]],
	['drivermanager','驱动管理','曹杨','module','avhips_proj',[]],
	['sysrepair','系统修复','周吉文','module','sysrepair_proj',[]],
	['antivirus','杀毒模块','赵欣','module','antivirus_proj',[]],
	['bdkv','杀毒主程序','易善鸿','module','avmain_proj',[]],
	['bd0001','驱动模块','曹杨','module','avdriver_proj',[]],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','base','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','middle','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','通用功能组件','杨彦召','middle','client_proj',[]],
	['client','产品中间层组件','杨彦召','middle','client_proj',[]],
	['commondll','公共dll库','刘恒','base','common_proj',[]],
	['bdnd','bdnd是什么','王超','module','ndmain_proj',[]],
	['syscleaner','系统清理','张巍','module','system_proj',[]],
	['sysaccelerator','系统加速','赫卫卿','module','system_proj',[]],
	['soacceleratorplugin','软件优化加速插件','赫卫卿','module','system_proj',[]],
	['socleanerplugin','系统优化清理插件','张巍','module','system_proj',[]],
	['somanager','软件优化管家','张凯','module','system_proj',[]],
	['soshortcutplugin','软件优化快捷插件','张凯','module','system_proj',[]],
	['swmanager','软件管理','张凯','module','system_proj',[]],
	['qmlib','qmlib是什么','张巍','middle','qmold_proj',[]],
	['qmgarbagecleaner','垃圾清理','张巍','module','qmold_proj',[]],
	['homepageplugins','主页插件','杨彦召','module','main_proj',[]],
	['mainframeplugins','框架插件','杨彦召','module','main_proj',[]],
	['main','极光主程序','杨彦召','module','main_proj',[]],
]

projects = {
	'X光':bdkv_slns,
	'极光':bdm_slns,
}

#选项名称，check还是radio，阶段，显示名称，tooltip名称，对应的值
bdkv_options = {
	#'prebuild':['check','before','清理','打包前的清理工作'],

	#'svn ':['radio','before',[('Ignore','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','1','default'),('checkout','所有相关工程从代码服务器重新签出','2')]],
	'svn ':['check','before','更新SVN','所有相关工程从代码服务器更新'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','1','default'),('rebuild','完全重新编译','2')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','1','default')]],

	'pack':['check','build','打包资源','重新打包资源'],
	'signdriver':['check','build','驱动签名','更新驱动签名'],
	'signkav':['check','build','卡巴签名','更新卡巴签名'],
	'signbaidu':['check','build','百度签名','更新百度签名'],
	'install':['check','build','生成安装包','生成安装包'],

	#'send':['radio','after',[('Ignore','生成的安装包不发送往任何地方','0'),('安装包归档','生成的安装包发送至归档目录',1,'default'),('mailme','生成安装包后给我发邮件',2)]],
	'send':['check','after','安装包归档','生成的安装包发送至归档目录'],

	'symadd':['check','after','符号归档','生成符号文件进行归档'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录'],
	#'postbuild':['check','after','清理','打包后的清理工作'],
}

bdm_options = {
	'prebuild':['check','before','清理','打包前的清理工作'],

	#'svn ':['radio','before',[('Ignore','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','1','default'),('checkout','所有相关工程从代码服务器重新签出','2')]],
	'svn ':['check','before','更新SVN','所有相关工程从代码服务器更新'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','1','default'),('rebuild','完全重新编译','2')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','1','default')]],

	'pack':['check','build','打包资源','重新打包资源'],
	'signbaidu':['check','build','百度签名','更新百度签名'],
	'install':['check','build','生成安装包','生成安装包'],

	#'send':['radio','after',[('Ignore','生成的安装包不发送往任何地方','0'),('安装包归档','生成的安装包发送至归档目录',1,'default'),('mailme','生成安装包后给我发邮件',2)]],
	'send':['check','after','安装包归档','生成的安装包发送至归档目录'],

	'symadd':['check','after','符号归档','生成符号文件进行归档'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录'],
	'postbuild':['check','after','清理','打包后的清理工作'],
}

build_options = {
	'X光': bdkv_options,
	'极光': bdm_options,
}

svn_codebase = [('Branch','基于特定分支构造',1),('Tag','基于特定Tag构造',2),('Trunk','基于主线构造',3,'default'),('Revision','基于特定Revision构造',4)]

build_depends = {
	'X光': svn_codebase,
	'极光': svn_codebase,
}

#每个sln的配置文件
bdkv_conf_files = {
	'commonlib':'BDMCommonLib',
	'commondll':'BDMCommonDll',
	'skin':'BDMSkin',
	'logicmisc':'BDMLogicMisc',
	'logicutils':'BDLogicUtils',
	'client':'BDMClient',
	'avcommon':'AVCommon',
	'filemon':'FileMon',
	'avhips':'AVHips',
	'drivermanager':'DriverManager',
	'sysrepair':'SYSRepair',
	'antivirus':'BDMAntiVirus',
	'bdkv':'BDKV',
	'bd0001':'BD0001',
}

bdm_conf_files = {
	'commonlib':'BDMCommonLib',
	'commondll':'BDMCommonDll',
	'skin':'BDMSkin',
	'logicmisc':'BDMLogicMisc',
	'logicutils':'BDLogicUtils',
	'client':'BDMClient',
	'qmlib':'QMlib',
	'bdnd':'BDND',
	'syscleaner':'SYSCleaner',
	'sysaccelerator':'BDMSYSAccelerator',
	'soacceleratorplugin':'BDMSOAcceleratorPlugin',
	'socleanerplugin':'BDMSOCleanerPlugin',
	'somanager':'BDMSOManager',
	'soshortcutplugin':'BDMSOShortcutPlugin',
	'swmanager':'BDMSWManager',
	'qmgarbagecleaner':'QMGarbageCleaner',
	'homepageplugins':'BDMHomePagePlugins',
	'mainframeplugins':'BDMMainFramePlugins',
	'main':'BDMMain',
}

build_conf_files = {
	'X光': bdkv_conf_files,
	'极光': bdm_conf_files,
}