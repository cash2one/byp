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
	['commonlib','公共lib库','刘恒','base',0,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','易善鸿','base',0,[]],
	['logicmisc','产品中间层组件','杨彦召','base',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','base',1,[]],
	['client','产品中间层组件','杨彦召','middle',1,[]],
	['commondll','公共dll库','刘恒','middle',1,[]],
	['avcommon','杀毒公共模块','务孟庆','module',1,[]],
	['filemon','文件监控模块','武广柱','module',1,[]],
	['avhips','主动防御模块','曹杨','module',1,[]],
	['drivermanager','驱动管理模块','曹杨','module',1,[]],
	['sysrepair','系统修复模块','周吉文','module',1,[]],
	['antivirus','杀毒模块','赵欣','module',1,[]],
	['bdkv','杀毒主程序模块','易善鸿','module',1,[]],
	['bd0001','驱动模块','曹杨','module',1,[]],
	['defense','攻防模块','时永昌','module',1,[]],
    ['attack','攻防模块','时永昌','module',1,[]],
    ['repair','修复模块','时永昌','module',1,[]],
    ['bdkitUtils','bdkit模块','时永昌','module',1,[]],
    ['websafe','websafe模块','务孟庆','module',0,[]],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','base',0,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','易善鸿','base',0,[]],
	['logicmisc','产品中间层组件','杨彦召','base',1,['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','产品中间层组件','杨彦召','base',1,[]],
	['client','产品中间层组件','杨彦召','middle',1,[]],
	['commondll','公共dll库','刘恒','middle',1,[]],
	['syscleanerlib','系统清理模块Lib','张巍','module',1,[]],
	['luaVM','lua脚本引擎','张巍','module',1,[]],
	['syscleaner','系统清理模块','张巍','module',1,[]],
	['soacceleratorlib','软件优化加速Lib','位广军','module',1,[]],
	['soacceleratorplugin','软件优化加速插件','位广军','module',1,[]],
	['swmanager','软件管理模块','张靖','module',1,[]],
	['main','卫士主程序','杨彦召','module',1,[]],
    ['trojanscan','木马扫描','易善鸿','module',1,[]],
    ['antivirusGJ','卫士查杀合入模块','赵欣','module',0,[]],
    ['drivermanager','驱动管理模块','曹杨','module',0,[]],
    ['avhips','主动防御模块','曹杨','module',0,[]],
    ['bd0001','驱动模块','曹杨','module',0,[]],
    ['patcher','漏洞修复模块','赵北宁','module',1,[]],
    ['attack','攻防模块','时永昌','module',0,[]],
    ['bdkitUtils','bdkit模块','时永昌','module',0,[]],
]

projects = {
	'杀毒':bdkv_slns,
	'卫士':bdm_slns,
}

#选项名称，check还是radio，阶段，显示名称，tooltip名称，对应的值
bdkv_options = {
	#'prebuild':['check','before','清理','打包前的清理工作','default'],
	'prebuild':['radio','before',[('不清理','打包前不进行任何清理工作','0'),('清理','打包前仅清理旧文件和日志','1'),('完全清理','打包前清理所有生成文件','2','default')]],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','3','default'),('checkout','所有产品关联工程从代码服务器重新签出','4'),('xcheck','仅所选工程从代码服务器重新签出','5')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新','default'],

	'rewriteversion':['check','before','dailybuild','此次打包更新dailybuild号','default'],
    
    'locksvn':['check','before','锁定SVN','禁止SVN代码提交'],

    'rcgen':['check','before','修复版本RC','重新生成产品相关的版本信息','default'],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','2','default')]],
	'build':['check','build','编译','选中工程全部重新编译','default'],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2','default'),('all','全部进行编译','3')]],

	'ignorefault':['check','build','无人值守','不提示编译和打包错误，但仍然完成整个编译流程'],

	'pack':['check','build','打包资源','重新打包资源','default'],
	#'signdriver':['check','build','驱动签名','更新驱动签名','default'],
	#'signkav':['check','build','卡巴签名','更新卡巴签名','default'],
	#'signbaidu':['check','build','百度签名','更新百度签名','default'],
	
    'rebase':['check','build','ImageBase修复','修改模块基地址并绑定以提高程序加载速度','default'],

	'sign':['check','build','二进制签名','对打包生成的二进制文件进行签名','default'],
	'install':['check','build','安装包','生成安装包','default'],
	
    'install_mini':['check','build','迷你下载器','同时生成迷你下载器（在线安装包）'],
	'install_full':['check','build','全量包','同时生成带全量病毒库的安装包'],
	'install_update':['check','build','升级测试包','同时生成升级测试安装包'],
	'install_silence':['check','build','静默包','生成静默安装包，安装包将带有silent字样'],

    'installermd5':['check','after','安装包Md5','生成安装包的Md5校验信息'],

	'send':['check','after','安装包归档','安装包发送至归档目录','default'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名','default'],

    'verify':['check','after','二进制校验','校验生成的二进制文件的完整性、版本、签名等是否正确'],
    'verifyinstaller':['check','after','安装包校验','校验安装包是否生成、版本、签名等是否正确'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档','default'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录','default'],
    
    'releasesvn':['check','after','释放SVN','重新允许SVN提交操作'],

    'sendmail':['check','after','邮件通知','发送打包概况邮件，仅适用于无人值守时'],
	
    #'postbuild':['check','after','清理','打包后的清理工作','default'],
    
    'xmarkup':['check','after','XMarkup','仅标记选中的解决方案'],
}

bdm_options = {
	#'prebuild':['check','before','清理','打包前的清理工作','default'],
	'prebuild':['radio','before',[('不清理','打包前不进行任何清理工作','0'),('清理','打包前仅清理旧文件和日志','1'),('完全清理','打包前清理所有生成文件','2','default')]],

	'svn':['radio','before',[('不更新SVN','不进行任何svn操作','0'),('update','所有相关工程从代码服务器更新','3','default'),('checkout','所有产品关联工程从代码服务器重新签出','4'),('xcheck','仅所选工程从代码服务器重新签出','5')]],
	#'svn':['check','before','更新SVN','所有相关工程从代码服务器更新','default'],

	'rewriteversion':['check','before','dailybuild','此次打包更新dailybuild号','default'],

    'locksvn':['check','before','锁定SVN','禁止SVN代码提交'],

    'rcgen':['check','before','修复版本RC','重新生成产品相关的版本信息','default'],

	#'build':['radio','build',[('不编译','不进行编译','0'),('build','全部增量编译','2','default')]],
	'build':['check','build','编译','选中工程全部重新编译','default'],

	'buildtype':['radio','build',[('debug','只编译debug','1'),('release','只编译release','2','default'),('all','全部进行编译','3')]],
	
	'ignorefault':['check','build','无人值守','不提示编译和打包错误，但仍然完成整个编译流程'],
	
	'pack':['check','build','打包资源','重新打包资源','default'],
	#'sign':['check','build','百度签名','更新百度签名','default'],
	
    'rebase':['check','build','ImageBase修复','修改模块基地址并绑定以提高程序加载速度','default'],

	'sign':['check','build','二进制签名','对打包生成的二进制文件进行签名','default'],
	'install':['check','build','安装包','生成安装包','default'],
	
    'install_mini':['check','build','迷你下载器','同时生成迷你下载器（在线安装包）'],
	'install_update':['check','build','升级测试包','同时生成升级测试安装包'],
	'install_silence':['check','build','静默包','生成静默安装包，安装包将带有silent字样'],

    'installermd5':['check','after','安装包Md5','生成安装包的Md5校验信息'],

	'send':['check','after','安装包归档','安装包发送至归档目录','default'],
	'signinstaller':['check','after','安装包签名','对安装包进行签名','default'],

    'verify':['check','after','二进制校验','校验生成的二进制文件的完整性、版本、签名等是否正确'],
    'verifyinstaller':['check','after','安装包校验','校验安装包是否生成、版本、签名等是否正确'],

	'symadd':['check','after','符号归档','生成的符号文件进行归档','default'],
	'commit':['check','after','提交basic','向代码服务器提交baisc目录','default'],

    'releasesvn':['check','after','释放SVN','重新允许SVN提交操作'],

    'sendmail':['check','after','邮件通知','发送打包概况邮件，仅适用于无人值守时'],

	#'postbuild':['check','after','清理','打包后的清理工作','default'],
	
	'xmarkup':['check','after','XMarkup','仅标记选中的解决方案','default'],
}

build_options = {
	'杀毒': bdkv_options,
	'卫士': bdm_options,
}

#支持的代码基依赖
bdkv_svn_codebase = [('Branch','基于特定Branch，输入Branch名称',1,'default'),('Tag','基于特定Tag，输入Tag名称',2),('Trunk','基于主线构造',3),('Revision','基于Revision，输入开发线;Revision号',4)]
bdm_svn_codebase = [('Branch','基于特定Branch，输入Branch名称',1),('Tag','基于特定Tag，输入Tag名称',2),('Trunk','基于主线构造',3,'default'),('Revision','基于Revision，输入开发线;Revision号',4)]

build_depends = {
	'杀毒': bdkv_svn_codebase,
	'卫士': bdm_svn_codebase,
}

#支持的版本标记选项
svn_markup_code = [('None','不标记此版本',0,'default'),('+Branch','以此版本新建Branch',1),('+Tag','以此版本新建Tag',2),('-Branch','删除指定Branch',3),('-Tag','删除指定Tag',4)]

markup_options = {
	'杀毒': svn_markup_code,
	'卫士': svn_markup_code,
}

#默认版本号
bdkv_default_version = '1.2.0.$auto'
bdm_default_version = '1.0.0.$auto'

default_version = {
	'杀毒':bdkv_default_version,
	'卫士':bdm_default_version,
}

#默认supplyid
bdkv_default_supplyid = 'm10001,n10000,f10015'
bdm_default_supplyid = 'm10001,n10000,f10015'

default_supplyid = {
	'杀毒':bdkv_default_supplyid,
	'卫士':bdm_default_supplyid,
}

#默认版本标记细节
bdkv_svn_default_markup_details = 'bdkv_$revision_$version_$timestamp'
bdm_svn_default_markup_details = 'bdm_$revision_$version_$timestamp'

markup_details = {
	'杀毒':bdkv_svn_default_markup_details,
	'卫士':bdm_svn_default_markup_details,
}

#默认打包原因
bdkv_default_build_reason = 'BaiduSd DB'
bdm_default_build_reason = 'BaiduAn DB'

default_build_reason = {
	'杀毒':bdkv_default_build_reason,
	'卫士':bdm_default_build_reason,
}

#默认使用者邮箱
bdkv_default_user_email = 'sw_aq@baidu.com'
bdm_default_user_email = 'sw_xt@baidu.com'

default_user_email = {
	'杀毒':bdkv_default_user_email,
	'卫士':bdm_default_user_email,
}

#默认版本构造细节
bdkv_default_cbdetail = '1.0beta3_dev'
bdm_default_cbdetail = 'HEAD'

default_cbdetail = {
	'杀毒':bdkv_default_cbdetail,
	'卫士':bdm_default_cbdetail,
}

#默认归档根目录
bdkv_archive_base = '$share/public/kvdailybuild/$version'
bdm_archive_base = '$share/public/dailybuild/$version'

default_archive_base = {
	'杀毒':bdkv_archive_base,
	'卫士':bdm_archive_base,
}
