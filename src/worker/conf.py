"""
@author 
@date	2012-11-9
@desc
	conf gj project build
	
@brief
	add some macros for bdkv product by tomas 2013-01-15
	add other more macros by tomas ...
"""

buildver_headerfile = "../include/CommonInclude/BuildVer.h"
buildver_definefile = "../include/CommonInclude/BDMVersion.h"
build_commonpath="./dailybuild/common_proj/Projects"
sln_commonname="BDMCommon.sln"
build_path="./dailybuild/main_proj/Projects" 
sln_name="BDMMain.sln"
build_liveuppath="./dailybuild/skin_proj/trunk/Projects"
sln_liveupname="BDMSkin.sln"
errfile="err.log"
wrnfile="warning.log"
logfile="build.log"
svnfile="svnNumber.txt"
build_tool="vcbuild"
build_flags=' /rebuild /time /M16 /logfile:%s /errfile:%s /wrnfile:%s %s '%(logfile,errfile,wrnfile,sln_name)
build_flags_liveup=' /rebuild /time /M16 /logfile:%s /errfile:%s /wrnfile:%s %s '%(logfile,errfile,wrnfile,sln_liveupname)
build_flags_common=' /rebuild /time /M16 /logfile:%s /errfile:%s /wrnfile:%s %s '%(logfile,errfile,wrnfile,sln_commonname)
needSign=True

build_tpl="""
current time: %s<br>
=================err_msg==============<br>
%s<br>
=================wrn_msg============<br>
%s<br>
=================build complete=========<br>
%s<br>
"""

cerf_addr='m1-scm-cluster-test03.m1.baidu.com:8111'
sign_file_exts='*.exe,*.dll,*.sys'
sign_file_product=u'百度卫士'
kvsign_file_product=u'百度杀毒'
sign_conf_file='./BuildSwitch/Signature.xml'
kvsign_conf_file='./BuildSwitch/KVSignature.xml'

verify_log_file = './AutoBuild/BinVerify.txt'
kvverify_log_file = './AutoBuild/KVBinVerify.txt'

exist_verify_file = './AutoBuild/FileVerify.xml'
kvexist_verify_file = './AutoBuild/KVFileVerify.xml'

build_rpt="build_rpt.txt"

checklog_file = "./AutoBuild/checklog.conf"
kvchecklog_file = "./AutoBuild/kvchecklog.conf"

debug_path='../Output/binDebug/'
kvdebug_path="../KVOutput/binDebug/"
debugList=["*.exe","*.dll","plugins","res","*.xml","*.png"]

bin_path='../Output/binRelease/'
kvbin_path='../KVOutput/binRelease/'
binList=["*.exe","*.dll","plugins","res","*.xml","*.png"]
pdbList=["*.pdb"]

setup_path='./setup/'
kvsetup_path='./kvsetup/'
setupList=["*.exe"]

log_path="./AutoBuild/err/"
kvlog_path="./AutoBuild/kverr/"
logList=["*.log"]

ouputDirName="gj_%d_%s_%s"
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
scp_flags="pscp -r -P 9922 -pw browseros  %s root@10.1.149.132:/data/wwwroot/gj"
buildIdFile="./AutoBuild/buildId.txt"
kvBuildIdFile="./AutoBuild/kvbuildId.txt"
versionBuildIdFile="./AutoBuild/versionBuildId.txt"
kvVersionBuildIdFile="./AutoBuild/kvVersionBuildId.txt"

#The following two lines DO NOT have spelling errors,merging daily and custom builds
customBuildIdFile="./AutoBuild/buildId.txt"
kvCustomBuildIdFile="./AutoBuild/kvbuildId.txt"

bdm_nsifile_daily="../Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_version="../Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_partial="../Tools/SetupScript/BDM_setup.nsi"
bdm_nsifile_buildline="../Tools/SetupScript/include/buildline.nsi"

bdkv_nsifile_daily="../Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_version="../Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_partial="../Tools/KVSetupScript/BDKV_setup.nsi"
bdkv_nsifile_buildline="../Tools/KVSetupScript/include/buildline.nsi"

webUrl="http://10.1.149.132:33002/"
fromaddr="tongyang@baidu.com"
toaddr=["tongyang@baidu.com"]
#toaddr=["yihongzhang"]
mailTitle="【gj】每日自动编译(%s)"
binFile="bin.txt"
pdbFile="pdb.txt"
setupFile="setup.txt"
debugFile="debug.txt"
outputMsg="""
%s
"""
bodyfmt="""
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<style type="text/css">
body {font-family: 微软雅黑;}
</style>
</head>
<body>
<p align="right"><font color="#9d1400" size="-1">SYSTEM TIME:%s</font></p>
<br/>
<p align="center"><font color="#040748" size="+2">UBrowser Daily Auto Build</font></p>
<ul><li><h4>Basic Information</h4></li></ul>
<div style="margin-left:30px">
<table border="1" cellpadding="0">
<tr>
<td align="center" bgcolor="#D7D7D7">Build ID</td>
<td align="center" bgcolor="#EFEFEF">%s</td>
</tr>
<tr>
<td align="center" bgcolor="#D7D7D7">SVN Number</td>
<td align="center" bgcolor="#EFEFEF">%s</td>
</tr>
<tr>
<td align="center" bgcolor="#D7D7D7">bin zip path</td>
<td align="center" bgcolor="#EFEFEF"><a href="%s">%s</a></td>
</tr>
<tr>
<td align="center" bgcolor="#D7D7D7">nsis package path</td>
<td align="center" bgcolor="#EFEFEF"><a href="%s">%s</a></td>
</tr>
</table>
</div>
<ul><li><h4>Compile information</h4></li></ul>
<div style="margin-left:30px">%s</div>
<div style="margin-left:30px;margin-top:30px"><font color="#9d1400" size="-1">Automatic e-mail, don't reply，<a href="http://10.1.149.132:33001/waterfall">more information</a></font></div>
</body>
</html>
"""
smtp_host="proxy-in.baidu.com"

ver_company_name = u'百度在线网络技术（北京）科技有限公司'
ver_legal_trademarks = 'Baidu'
ver_copyright = 'Copyright ? 2012-2017 Baidu. All Rights Reserved.'
ver_product_manager = 'Baidu Manager'
ver_product_antivirus = u'百度杀毒'

rclist_file = './AutoBuild/rcdef.xml'

mgr_official_sign_excluded_dir = []

kv_official_sign_excluded_dir = ['..\\kvoutput\\binrelease\\kav\\',
								'..\\kvoutput\\binrelease\\kavdrivers\\',
								'..\\kvoutput\\binrelease\\microsoft.vc80.atl\\',
								'..\\kvoutput\\binrelease\\microsoft.vc80.crt\\',
                                '..\\kvoutput\\binrelease\\bdmantivirus\\kavupdate\\',]

