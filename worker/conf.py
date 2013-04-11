"""
@author tomas
@date	2013-04-12
@desc
	main configuration file
	
@brief
	
"""

buildver_headerfile = "../../basic/include/CommonInclude/BuildVer.h"
buildver_definefile = "../../basic/include/CommonInclude/BDMVersion.h"

cerf_addr='m1-scm-cluster-test03.m1.baidu.com:8111'
sign_file_exts='*.exe,*.dll,*.sys'
sign_file_product=u'百度卫士'
kvsign_file_product=u'百度杀毒'
sign_conf_file='./buildswitch/Signature.xml'
kvsign_conf_file='./buildswitch/KVSignature.xml'

verify_log_file = '../output/BinVerify.txt'
kvverify_log_file = '../output/KVBinVerify.txt'

exist_verify_file = './conf/FileVerify.xml'
kvexist_verify_file = './conf/KVFileVerify.xml'

checklog_file = "./conf/checklog.conf"
kvchecklog_file = "./conf/kvchecklog.conf"

debug_path='../../basic/Output/binDebug/'
kvdebug_path="../../basic/binDebug/"
debugList=["*.exe","*.dll","plugins","res","*.xml","*.png"]

bin_path='../../basic/Output/binRelease/'
kvbin_path='../../basic/KVOutput/binRelease/'
binList=["*.exe","*.dll","plugins","res","*.xml","*.png"]
pdbList=["*.pdb"]

setup_path='../output/setup/'
kvsetup_path='../output/kvsetup/'
setupList=["*.exe"]

log_path="../output/err/"
kvlog_path="../output/kverr/"
logList=["*.log"]

severDirName_daily="1.0.0.%d"
severDirName_version="1.0.1.%d"
severDirName_partial="1.0.0.%d"
ftpPathNameR= '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'DailyBuild' +'\\' 
ftpKVPathNameR= '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'KVDailyBuild' +'\\' 
ftpVersionPathNameR = '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'VersionBuild' +'\\'
ftpVersionKVPathNameR = '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'KVVersionBuild' +'\\'

#The following two lines DO NOT have spelling errors,merging daily and custom builds
ftpCustomPathNameR = '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'DailyBuild' +'\\'
ftpCustomKVPathNameR = '\\\\'+'192.168.10.242'+'\\' + 'public' + '\\' + 'KVDailyBuild' +'\\'

ftpPathNameD= '\\'+'Debug' +'\\'
ftpPathNameRR= '\\'+'Release' +'\\'
ftpPathNameLog= '\\'+'Log' +'\\'

buildIdFile="../../basic/tools/AutoBuild/buildId.txt"
kvBuildIdFile="../../basic/tools/AutoBuild/kvbuildId.txt"
versionBuildIdFile="../../basic/tools/AutoBuild/versionBuildId.txt"
kvVersionBuildIdFile="../../basic/tools/AutoBuild/kvVersionBuildId.txt"

#The following two lines DO NOT have spelling errors,merging daily and custom builds
customBuildIdFile="../../basic/tools/AutoBuild/buildId.txt"
kvCustomBuildIdFile="../../basic/tools/AutoBuild/kvbuildId.txt"

bdm_nsifile_daily="../../basic/Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_version="../../basic/Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_partial="../../basic/Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_buildline="../../basic/Tools/SetupScript/include/buildline.nsi"

bdkv_nsifile_daily="../../basic/Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_version="../../basic/Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_partial="../../basic/Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_buildline="../../basic/Tools/KVSetupScript/include/buildline.nsi"

fromaddr="liuheng@baidu.com"
toaddr=["liuheng@baidu.com"]

smtp_host="proxy-in.baidu.com"

ver_company_name = u'百度在线网络技术（北京）科技有限公司'
ver_legal_trademarks = 'Baidu'
ver_copyright = 'Copyright ? 2012-2017 Baidu. All Rights Reserved.'
ver_product_manager = 'Baidu Manager'
ver_product_antivirus = u'百度杀毒'

rclist_file = './AutoBuild/rcdef.xml'

mgr_official_sign_excluded_dir = []

kv_official_sign_excluded_dir = ['..\\..\\basic\\kvoutput\\binrelease\\kav\\',
								'..\\..\\basic\\kvoutput\\binrelease\\kavdrivers\\',
								'..\\..\\basic\\kvoutput\\binrelease\\microsoft.vc80.atl\\',
								'..\\..\\basic\\kvoutput\\binrelease\\microsoft.vc80.crt\\',
                                '..\\..\\basic\\kvoutput\\binrelease\\bdmantivirus\\kavupdate\\',]

kvsign_excluded_dir = ['..\\kvoutput\\binrelease\\kavdrivers\\udinstaller32.exe',
                      '..\\kvoutput\\binrelease\\kavdrivers\\udinstaller64.exe',]

kvsign_kav_excluded_dir = ['..\\kvoutput\\binrelease\\kavdrivers\\udinstaller32.exe',
                          '..\\kvoutput\\binrelease\\kavdrivers\\udinstaller64.exe',]


#总的工程根目录
sln_root = '..\\..\\'
bin_path = '..\\bin\\'
