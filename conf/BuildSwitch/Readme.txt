0.readme for xbuild by tomas

1.������Ҫ����BuildStep.xml���ö�����svn�汾����ϵͳ��vcbuild����ϵͳ��Python2.X֧�֣�X>=5��������Ҫ��װpywin32��չ�����뱣֤%PATH%�а���svn.exe��vcbuild.exe��python.exe

2.�������������ļ���
	AutoBuild/checklog.conf			������Ŀ�������ϵͳ��solution����������
	AutoBuild/kvchecklog.conf		X����Ŀ�������ϵͳ��solution����������
	AutoBuild/FileVerify.xml		������Ŀ�ļ�������У���б�
	AutoBuild/KVFileVerify.xml		X����Ŀ�ļ�������У���б�
	BuildSwitch/%sln%.xml			ÿ��������Ҫ�����solution�����ļ�
	BuildSwitch/BuildStep.xml		�������ͺͱ��벽�趨��
	BuildSwtich/KVSignature.xml		�ٷ�ǩ������

3.����BuildStep.xml���������ֵ�Ժ��壺
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

4.ʹ��ǰ����BuildStep.xml�е������Ƿ���������build����

5.������б��루build�������ҳ����˱�����󣬽��������½��У���ʾ������