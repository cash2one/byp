# coding=UTF-8
"""
@author thomas
@date    2013-03-31
@desc
	project configuration
    
@brief
    
"""


#sln名称，介绍，负责人，分类，默认是否编译(1,0)，被哪些工程依赖
bdkv_slns = [
	['commonlib','公共lib库','刘恒','base',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle',1,[]],
	['logicmisc','产品中间层组件','杨彦召','middle',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','middle',1,[]],
	['client','产品中间层组件','杨彦召','middle',1,[]],
	['commondll','公共dll库','刘恒','base',1,[]],
	['avcommon','杀毒公共模块','务孟庆','module',1,[]],
	['filemon','文件监控模块','武广柱','module',1,[]],
	['avhips','主动防御模块','曹杨','module',1,[]],
	['drivermanager','驱动管理模块','曹杨','module',1,[]],
	['sysrepair','系统修复模块','周吉文','module',1,[]],
	['antivirus','杀毒模块','赵欣','module',1,[]],
	['bdkv','杀毒主程序模块','易善鸿','module',1,[]],
	['bd0001','驱动模块','曹杨','module',1,[]],
	['defense','攻防模块','时永昌','module',1,[]],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','base',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','middle',1,[]],
	['logicmisc','产品中间层组件','杨彦召','middle',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','middle',1,[]],
	['client','产品中间层组件','杨彦召','middle',1,[]],
	['commondll','公共dll库','刘恒','base',1,[]],
	#['bdnd','bdnd是什么','王超','module',1,[]],
	['syscleaner','系统清理模块','张巍','module',1,[]],
	#['sysaccelerator','系统加速模块','赫卫卿','module',1,[]],
	['soacceleratorplugin','软件优化加速插件','赫卫卿','module',1,[]],
	#['socleanerplugin','系统优化清理插件','张巍','module',1,[]],
	#['somanager','软件优化管家','张凯','module',1,[]],
	#['soshortcutplugin','软件优化快捷插件','张凯','module',1,[]],
	['swmanager','软件管理模块','张凯','module',1,[]],
	['main','极光主程序','杨彦召','module',1,[]],
    ['trojanscan','木马扫描','易善鸿','module',1,[]],
    #['antivirusGJ','极光查杀合入模块','赵欣','module',1,[]],
    ['drivermanager','驱动管理模块','曹杨','module',1,[]],
    ['avhips','主动防御模块','曹杨','module',1,[]],
    ['bd0001','驱动模块','曹杨','module',1,[]],
    ['patcher','漏洞修复模块','赵北宁','module',1,[]],
    ['patcherplugin','漏洞修复插件','赵北宁','module',1,[]],
]

projects = {
	'X光':bdkv_slns,
	'极光':bdm_slns,
}

#选项名称，check还是radio，阶段，显示名称，tooltip名称，对应的值
bdkv_options = {
	#'prebuild':['check','before','清理','打包前的清理工作','default'],
	'prebuild':['radio','before',[('不清理','打包前不进行任何清理工作','0'),('清理','打包前仅清理旧文件和日志','1'),('完全清理','打包前清理所有生成文件','2','default')]],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','3','default'),('checkout','所有相关工程从代码服务器重新签出','4')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新','default'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('不更新版本','此次打包不更新版本','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
    
    'locksvn':['check','before','锁定SVN','整个版本构建期间禁止代码提交'],

    'rcgen':['check','before','修复版本RC','重新生成产品相关的版本信息','default'],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','2','default'),('rebuild','完全重新编译','4')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','2','default'),('重新编译','全部完全重新编译','4')]],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2','default'),('all','全部进行编译','3')]],

	'ignorefault':['check','build','无人值守','不提示编译和打包错误，但仍然完成整个编译流程'],

	'pack':['check','build','打包资源','重新打包资源','default'],
	#'signdriver':['check','build','驱动签名','更新驱动签名','default'],
	#'signkav':['check','build','卡巴签名','更新卡巴签名','default'],
	#'signbaidu':['check','build','百度签名','更新百度签名','default'],
	
    'rebase':['check','build','ImageBase修复','修改模块基地址并绑定以提高程序加载速度','default'],

	'sign':['check','build','文件签名','对打包生成的文件进行签名','default'],
	'install':['check','build','安装包','生成安装包','default'],
	
    'install_mini':['check','build','迷你下载器','同时生成迷你下载器（在线安装包）'],
	'install_full':['check','build','全量包','同时生成带全量病毒库的安装包'],
	'install_update':['check','build','升级测试包','同时生成升级测试安装包'],
	'install_silence':['check','build','静默包','同时生成静默安装包'],

	'send':['radio','after',[('不归档','安装包不发送往任何地方','0'),('dailybuild','安装包发送至dailybuild目录归档',1,'default'),('versionbuild','安装包发送至versionbuild目录归档',2),]],
	#'send':['check','after','安装包归档','安装包发送至归档目录','default'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名','default'],

    'verify':['check','after','文件校验','校验生成的二进制文件的完整性、版本、签名等是否正确'],
    'verifyinstaller':['check','after','安装包校验','校验安装包是否生成、版本、签名等是否正确'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档','default'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录','default'],
    
    'releasesvn':['check','after','释放SVN','重新允许SVN提交操作'],

    'sendmail':['check','after','邮件通知','发送打包概况邮件，仅适用于无人值守时'],
	
    #'postbuild':['check','after','清理','打包后的清理工作','default'],
}

bdm_options = {
	#'prebuild':['check','before','清理','打包前的清理工作','default'],
	'prebuild':['radio','before',[('不清理','打包前不进行任何清理工作','0'),('清理','打包前仅清理旧文件和日志','1'),('完全清理','打包前清理所有生成文件','2','default')]],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','3','default'),('checkout','所有相关工程从代码服务器重新签出','4')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新','default'],

	#'rewriteversion':['radio','before',[('Ignore','此次打包不更新版本号','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],
	'rewriteversion':['radio','before',[('不更新版本','此次打包不更新版本','0'),('dailybuild','此次打包更新dailybuild号','1','default'),('versionbuild','此次打包更新versionbuild号','2')]],

    'locksvn':['check','before','锁定SVN','整个版本构建期间禁止代码提交'],

    'rcgen':['check','before','修复版本RC','重新生成产品相关的版本信息','default'],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','2','default'),('rebuild','完全重新编译','4')]],
	'build':['radio','build',[('不编译','不进行编译','0'),('编译','全部增量编译','2','default'),('重新编译','全部完全重新编译','4')]],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2'),('all','全部进行编译','3','default')]],
	
	'ignorefault':['check','build','无人值守','不提示编译和打包错误，但仍然完成整个编译流程'],
	
	'pack':['check','build','打包资源','重新打包资源','default'],
	#'sign':['check','build','百度签名','更新百度签名','default'],
	
    'rebase':['check','build','ImageBase修复','修改模块基地址并绑定以提高程序加载速度','default'],

	'sign':['check','build','文件签名','对打包生成的文件进行签名','default'],
	'install':['check','build','安装包','生成安装包','default'],
	
    'install_mini':['check','build','迷你下载器','同时生成迷你下载器（在线安装包）'],
	'install_update':['check','build','升级测试包','同时生成升级测试安装包'],
	'install_silence':['check','build','静默包','同时生成静默安装包'],

	'send':['radio','after',[('不归档','安装包不发送往任何地方','0'),('dailybuild','安装包发送至dailybuild目录归档',1,'default'),('versionbuild','安装包发送至versionbuild目录归档',2),]],
	#'send':['check','after','安装包归档','安装包发送至归档目录','default'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名','default'],

    'verify':['check','after','文件校验','校验生成的二进制文件的完整性、版本、签名等是否正确'],
    'verifyinstaller':['check','after','安装包校验','校验安装包是否生成、版本、签名等是否正确'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档','default'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录','default'],

    'releasesvn':['check','after','释放SVN','重新允许SVN提交操作'],

    'sendmail':['check','after','邮件通知','发送打包概况邮件，仅适用于无人值守时'],

	#'postbuild':['check','after','清理','打包后的清理工作','default'],
}

build_options = {
	'X光': bdkv_options,
	'极光': bdm_options,
}

#支持的代码基依赖
svn_codebase = [('Branch','基于特定Branch，输入Branch名称',1),('Tag','基于特定Tag，输入Tag名称',2),('Trunk','基于主线构造',3,'default'),('Revision','基于主线Revision，输入Revision号',4)]

build_depends = {
	'X光': svn_codebase,
	'极光': svn_codebase,
}

#支持的版本标记选项
svn_markup_code = [('None','不标记此版本',0,'default'),('+Branch','以此版本新建Branch',1),('+Tag','以此版本新建Tag',2),('-Branch','删除指定Branch',3),('-Tag','删除指定Tag',4)]

markup_options = {
	'X光': svn_markup_code,
	'极光': svn_markup_code,
}
