"""
@author    tomas
@date    2013-04-19
@desc
    verify vcproj optimization configurations
    
"""

import sys, fileop, conf, xml.dom.minidom

bdm_proj_dir = [
                 
                 ]

bdm_proj_excluded_dir = [
                          
                          ]

bdkv_proj_dir = [
                 'common_proj',
                 'skin_proj',
                 'client_proj',
                 'avcommon_proj',
                 'avfilemon_proj',
                 'avhips_proj',
                 'sysrepair_proj',
                 'antivirus_proj',
                 'avmain_proj',
                 'avdriver_proj',
                 ]

bdkv_proj_excluded_dir = [
                          
                          ]

def VerifyVcprojOptimizOptions(file):
    print file
    try:
        dom = xml.dom.minidom.parse(file,encoding='utf-8')
        root = dom.documentElement
        confs = root.getElementsByTagName('Configurations')
        print confs
    except Exception,e:
        print e

def main(argc, argv):
    if argc != 2:
        print 'usage: python vcproj_verify.py [product_nickname (bdm|bdkv)]'
        return
    
    if argv[1] == 'bdm':
        proj_dir = bdm_proj_dir
        excluded_dir = bdm_proj_excluded_dir
    elif argv[1] == 'bdkv':
        proj_dir = bdkv_proj_dir
        excluded_dir = bdkv_proj_excluded_dir
        
    for dir in proj_dir:
        fileop.FileOperation(conf.sln_root + dir,VerifyVcprojOptimizOptions,['*.vcproj'],excluded_dir)
    

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
