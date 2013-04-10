"""
@author yihongzhang
@date	2012-3-9
@desc

@brief
    1.merge bdm and bdkv update_version logic by tomas 2013-01-15
    2.add daily_build and version_build by tomas 2013-01-22 
    3.auto-modify version info by tomas 2013-02-25
"""
import sys,os,time,re,datetime
import conf
import comm
import time
import codecs

def update_h_build_info(FilePath, version_key, data_key, num, severtime):
        file_r = codecs.open(FilePath,"r","utf_16")
        list_line = file_r.readlines()
        file_r.close()
        print (list_line)
        for index in range(len(list_line)):
                if list_line[index].find(version_key)!= -1:
                        writeline = version_key + num + '\r\n'
                        list_line[index] = writeline
                elif list_line[index].find(data_key)!= -1:
                        writeline = data_key + 'TEXT'+'("'+ severtime + '")' + '\r\n'
                        list_line[index] = writeline
        file_w  = codecs.open(FilePath,"w","utf_16")
        file_w .writelines(list_line)
        file_w .close()

def update_nsis_build_info(FilePath, version_key, data_key, num, severtime):
        file_nsi_r = open(FilePath,'r')
        list_line = file_nsi_r.readlines()
        file_nsi_r.close()
        print (list_line)
        for index in range(len(list_line)):
                if list_line[index].find(version_key)!= -1:
                        writeline = version_key + '  "'+ num + '"'+'\n'
                        list_line[index] = writeline
                elif list_line[index].find(data_key)!= -1:
                        writeline = data_key + '  "' + severtime + '"' + '\n'
                        list_line[index] = writeline
        file_nsi_w = open(FilePath,'w')
        file_nsi_w.writelines(list_line)
        file_nsi_w.close()

def AddBuildId(buildIdFile):
    buildId=1
    if os.path.exists(buildIdFile):
        data=comm.getMsg(buildIdFile)
    try:
        buildId=str(int(data)+1)
    except:
        buildId="121"
    comm.saveFile(buildIdFile,buildId)
    return buildId

def update_buildver(num):
    buildverFile = conf.buildver_headerfile
    cont = '''//Auto-generated file by ../../Tools/AutoBuild/rewrite_version.py
//DO NOT EDIT!!
#ifndef __BUILD_VER_H_INCLUDED__
#define __BUILD_VER_H_INCLUDED__

#define VER_BUILD %s //Build Version

#endif // __BUILD_VER_H_INCLUDED__
''' % num
    
    comm.saveFile(buildverFile,cont)

def update_file_lines(FilePath, replacements,bVerbose):
        ifile = open(FilePath,'r')
        list_lines = ifile.readlines()
        ifile.close()
        for index in range(len(list_lines)):
            for (key,rep) in replacements:
                if (list_lines[index].find(key) != -1):
                    if bVerbose:
                        print '%s replaces with : %s' % (list_lines[index],rep)
                    list_lines[index] = rep + '\n'
        ofile = open(FilePath,'w')
        ofile.writelines(list_lines)
        ofile.close()
        
def update_version_define(buildline,buildnum):
    replacements = []
    verRelease = '#define VER_Release         %s' % buildnum
    verBuild = '#define VER_Build           %d' % buildline
    verBuildDateTime = '#define VER_ConstructDateTime   TEXT("%s")' % datetime.datetime.now().isoformat()
    replacements.append(('#define VER_Release',verRelease))
    replacements.append(('#define VER_Build',verBuild))
    replacements.append(('#define VER_ConstructDateTime',verBuildDateTime))
    update_file_lines(conf.buildver_definefile,replacements,True)
    
def update_product_version(nsiFile,product_version):
    replacements = []
    pv1 = 'VIProductVersion "%s"' % product_version
    pv2 = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"' % product_version
    pv3 = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"' % product_version
    replacements.append(('VIProductVersion ',pv1))
    replacements.append(('VIAddVersionKey /LANG=2052 "FileVersion" ',pv2))
    replacements.append(('VIAddVersionKey /LANG=2052 "ProductVersion" ',pv3))
    update_file_lines(nsiFile,replacements,True)

def main(argc,argv):
    if argc != 3:
        print 'usage:python rewrite_version.py <product_shortname (bdm|bdkv)> <build_type (daily|force)>'
        return
    
    buildIdFile = ''
    nsiFile = ''
    nsiBuildlineFile = ''
    buildline = 0
    productMacro = ''
    if argv[1].lower() == 'bdm':
        nsiBuildlineFile = conf.bdm_nsifile_buildline
        if argv[2].lower() == 'daily':
            buildIdFile = conf.buildIdFile
            nsiFile = conf.bdm_nsifile_daily
            buildline = 0
        elif argv[2].lower() == 'version':
            buildIdFile = conf.versionBuildIdFile
            nsiFile = conf.bdm_nsifile_version
            buildline = 1
        elif argv[2].lower() == 'partial':
            buildIdFile = conf.customBuildIdFile
            nsiFile = conf.bdm_nsifile_partial
            buildline = 0
    elif argv[1].lower() == 'bdkv':
        nsiBuildlineFile = conf.bdkv_nsifile_buildline
        if argv[2].lower() == 'daily':
            buildIdFile = conf.kvBuildIdFile
            nsiFile = conf.bdkv_nsifile_daily
            buildline = 0
        elif argv[2].lower() == 'version':
            buildIdFile = conf.kvVersionBuildIdFile
            nsiFile = conf.bdkv_nsifile_version
            buildline = 1
        elif argv[2].lower() == 'partial':
            buildIdFile = conf.kvCustomBuildIdFile
            nsiFile = conf.bdkv_nsifile_partial
            buildline = 0
    
    if buildIdFile and nsiFile:
        num = AddBuildId(buildIdFile)
        severtime = time.strftime("%Y-%m-%d %I:%M:%S")
        update_nsis_build_info(nsiFile, '!define RELEASE_VERSION', '!define BUILD_TIME',num,severtime)
        update_buildver(num)
        update_version_define(buildline,num)
        product_version = '1.0.%d.%s' % (buildline,num)
        update_product_version(nsiFile,product_version)
        
        buildlinestr = '!define BUILD_LINE  "%d"' % buildline
        comm.saveFile(nsiBuildlineFile,buildlinestr)

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))

