"""
@author    tomas
@date    2013-03-14
@desc
    verify product(file_exist,file_version,driver_sign,kav_sign,baidu_sign)

"""

import sys,os,userconf,fileop

def main(argc, argv):
    if argc != 2:
        print 'usage: python verifyproduct.py <product_shortname (bdm|bdkv)>'
    installdir = ''
    logfile = ''
    install_verify_list = ''
    datadir_verify_list = ''
    if argv[1] == 'bdm':
        installdir = userconf.mgr_install_dir
        logfile = userconf.mgr_verify_log_file
        install_verify_list = userconf.mgr_install_verify_file
        datadir_verify_list = userconf.mgr_datadir_verify_file
    elif argv[1] == 'bdkv':
        installdir = userconf.kv_install_dir
        logfile = userconf.kv_verify_log_file
        install_verify_list = userconf.kv_install_verify_file
        datadir_verify_list = userconf.kv_datadir_verify_file
    
    #install_folder_file_verify
    fileop.VerifyFileExist(installdir,['*.*'],argv[1],logfile,install_verify_list)
    #data_config_folder_file_verify
    fileop.VerifyFileExist(userconf.data_conf_dir,['*.*'],argv[1],logfile,datadir_verify_list)
    #installer_folder_file_version_verify
    fileop.VerifyFileVersion(installdir,['*.exe','*.dll','*.sys'],argv[1],logfile)
    if argv[1] == 'bdkv':
        #driver_sign_verify
        fileop.VerifyDriverSign(installdir,['*.exe'],'bdkv',logfile)
        #kav_sign_verify
        fileop.VerifyKavSign(installdir,['*.exe'],'bdkv',logfile)
    #baidu_official_sign_verify(please edit ./BuildSwitch/Signature.xml|KVSignature.xml)
    fileop.VerifyBaiduSign(installdir,['*.exe','*.dll','*.sys'],argv[1],logfile)
    
if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
