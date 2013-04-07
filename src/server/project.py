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

#sln名称，介绍，负责人，目录，被哪些工程依赖
bdkv_slns = [
	['commonlib','公共lib库','刘恒','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['bdlogicutils','产品中间层组件','杨彦召','client_proj',[]],
	['bdmclient','产品中间层组件','杨彦召','client_proj',[]],
	['bdmcommondll','公共dll库','刘恒','common_proj',[]],
	['avcommon','杀毒公共模块','务孟庆','avcommon_proj',[]],
	['filemon','文件监控','武广柱','avfilemon_proj',[]],
	['avhips','主动防御','曹杨','avhips_proj',[]],
	['drivermanager','驱动管理','曹杨','avhips_proj',[]],
	['sysrepair','系统修复','周吉文','sysrepair_proj',[]],
	['bdmantivirus','杀毒模块','赵欣','antivirus_proj',[]],
	['bdkv','杀毒主程序','易善鸿','avmain_proj',[]],
	['bd0001','驱动模块','曹杨','avdriver_proj',[]],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','通用功能组件','杨彦召','client_proj',[]],
	['bdmclient','产品中间层组件','杨彦召','client_proj',[]],
	['bdmcommondll','公共dll库','刘恒','common_proj',[]],
	['bdnd','bdnd是什么','王超','ndmain_proj',[]],
	['syscleaner','系统清理','张巍','system_proj',[]],
	['bdmsysaccelerator','系统加速','赫卫卿','system_proj',[]],
	['bdmsoacceleratorplugin','软件优化加速插件','赫卫卿','system_proj',[]],
	['bdmsocleanerplugin','系统优化清理插件','张巍','system_proj',[]],
	['bdmsomanager','软件优化管家','张凯','system_proj',[]],
	['bdmsoshortcutplugin','软件优化快捷插件','张凯','system_proj',[]],
	['bdmswmanager','软件管理','张凯','system_proj',[]],
	['qmlib','qmlib是什么','张巍','qmold_proj',[]],
	['qmgarbagecleaner','垃圾清理','张巍','qmold_proj',[]],
	['bdmhomepageplugins','主页插件','杨彦召','main_proj',[]],
	['bdmmainframeplugins','框架插件','杨彦召','main_proj',[]],
	['bdmmain','极光主程序','杨彦召','main_proj',[]],
]

projects = {
	'X光':bdkv_slns,
	'极光':bdm_slns,
}

bdkv_options = {
	'prebuild':['check','打包前清理','打包前清理'],
	'svn ':['radio',[('不处理svn','不处理svn','0'),('checkout','签出svn','1'),('update','更新svn','2')]],
	'rewriteversion':['radio',[('不更新版本号','不更新版本号','0'),('更新dailybuild号','更新dailybuild号','1'),('更新versionbuild号','更新versionbuild号','2')]],
	'build':['radio',[('不编译','不编译','0'),('build','增量编译','1'),('rebuild','完全重新编译','2')]],
	'pack':['check','压缩资源','压缩资源'],
	'signdriver':['check','驱动签名','驱动签名'],
	'signkav':['check','卡巴签名','卡巴签名'],
	'signbaidu':['check','百度签名','百度签名'],
	'install':['check','打包','打包'],
	'send':['radio',[('不送往任何地方','不送往任何地方','0'),('送至归档处','送至归档目录',1),('mailme','给我发邮件',2)]],
	'symadd':['check','符号归档','符号归档'],
	'commit':['check','提交basic目录','提交baisc目录'],
	'postbuild':['check','打包后清理','打包后清理'],
}

bdm_options = {
	'prebuild':['check','打包前清理','打包前清理'],
	'svn ':['radio',[('不处理svn','不处理svn','0'),('checkout','签出svn','1'),('update','更新svn','2')]],
	'rewriteversion':['radio',[('不更新版本号','不更新版本号','0'),('更新dailybuild号','更新dailybuild号','1'),('更新versionbuild号','更新versionbuild号','2')]],
	'build':['radio',[('不编译','不编译','0'),('build','增量编译','1'),('rebuild','完全重新编译','2')]],
	'pack':['check','压缩资源','压缩资源'],
	'signbaidu':['check','百度签名','百度签名'],
	'install':['check','打包','打包'],
	'send':['radio',[('不送往任何地方','不送往任何地方','0'),('送至归档处','送至归档目录',1),('mailme','给我发邮件',2)]],
	'symadd':['check','符号归档','符号归档'],
	'commit':['check','提交basic目录','提交baisc目录'],
	'postbuild':['check','打包后清理','打包后清理'],
}

build_options = {
	'X光': bdkv_options,
	'极光': bdm_options,
}