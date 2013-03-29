0.readme for xbuild by tomas

1.可能需要（视BuildStep.xml配置而定）svn版本管理系统，vcbuild构建系统和Python2.X支持（X>=5，可能需要安装pywin32扩展），请保证%PATH%中包含svn.exe、vcbuild.exe、python.exe

2.几个核心配置文件：
	AutoBuild/checklog.conf			极光项目纳入编译系统的solution名和责任人
	AutoBuild/kvchecklog.conf		X光项目纳入编译系统的solution名和责任人
	AutoBuild/FileVerify.xml		极光项目文件完整性校验列表
	AutoBuild/KVFileVerify.xml		X光项目文件完整性校验列表
	BuildSwitch/%sln%.xml			每个可能需要编译的solution配置文件
	BuildSwitch/BuildStep.xml		编译类型和编译步骤定义
	BuildSwtich/KVSignature.xml		官方签名配置

3.关于BuildStep.xml，各步骤键值对含义：
	prebuild				0-pass;1-simpleclean;2-fullclean
	svn					0-pass;1-forcecheckout;2-forceupdate;3-optionalcheckout;4-optionalupdate
	rewriteversion				0-pass;1-daily;2-version
	build					0-pass;1-rebuildrelease;2-buildrelease;3-optionalrebuildrelease;4-optionalbuildrelease
	pack					0-pass;1-packrelease
	sign					0-pass;1-signrelease;
	verify					0-pass;1-doit
	install					0-pass;1-doit
	signinstaller				0-pass;1-doit
	verifyinstaller  			0-pass;1-doit
	send					0-pass;1-daily;2-version
	symadd					0-pass;1-addrelease
	commit					0-pass;1-doit
	postbuild				0-pass

4.使用前请检查BuildStep.xml中的配置是否满足您的build需求

5.如果进行编译（build）步骤且出现了编译错误，将不再向下进行，提示并响铃