# coding=UTF-8
"""
@author thomas
@date	2011-12-14
@desc
	send file tools for Ubrowser
	
@brief
	1.merge bdm and bdkv ouput_send logic by liuheng 2013-01-15
	2.add daily_build and version_build 2013-01-22 
"""

import sys,os,time,re,shutil,glob,tarfile
import conf
import comm

def getBuildId(buildIdFile):
    if os.path.exists(buildIdFile):
        data=comm.getMsg(buildIdFile)
    try:
        ret=int(data)
    except:
        ret=1
    return ret

def gzFolder(foldername):
    aimfile=foldername+".tar"
    tar = tarfile.open(aimfile,"w")
    for item in os.listdir(foldername):
        addName=os.path.join(foldername,item)
        tar.add(addName,item)
    tar.close()
    return aimfile

def copyFiles(filepath,srclist,dest):
    """
        copy dir has bug
    """
    for item in srclist:
        srcpath=filepath+item
        filelist = glob.glob(srcpath)
        for item in filelist:
            if os.path.isfile(item):
                shutil.copy2(item,dest)
            elif os.path.isdir(item):
                baseName=os.path.basename(item)
                aimpath=os.path.join(dest,baseName)
                if not os.path.exists(aimpath):
                    os.mkdir(aimpath)
                cmd='xcopy /E  "%s"  "%s" '%(item,aimpath)
                os.popen(cmd)

def uploadFiles(file):
    os.popen(conf.scp_flags%(file),"w").write("y\r\n")

def main(argc, argv):
    if argc != 3:
        print 'usage:python send.py <product_shortname (bdm|bdkv)> <build_type (daily|force)>'
        return
    
    buildIdFile = ''
    ftpPathName = ''
    debugPath = ''
    binPath = ''
    logPath = ''
    setupPath = ''
    svrDirName = ''
    if argv[1].lower() == 'bdm':
        if argv[2].lower() == 'daily':
        	buildIdFile = conf.buildIdFile
        	ftpPathName = conf.ftpPathNameR
        	svrDirName = conf.severDirName_daily
        elif argv[2].lower() == 'version':
        	buildIdFile = conf.versionBuildIdFile
        	ftpPathName = conf.ftpVersionPathNameR
        	svrDirName = conf.severDirName_version
        elif argv[2].lower() == 'partial':
        	buildIdFile = conf.customBuildIdFile
        	ftpPathName = conf.ftpCustomPathNameR
        	svrDirName = conf.severDirName_partial
    	debugPath = conf.debug_path
    	binPath = conf.bin_path
    	logPath = conf.log_path
    	setupPath = conf.setup_path
    elif argv[1].lower() == 'bdkv':
        if argv[2].lower() == 'daily':
        	buildIdFile = conf.kvBuildIdFile
        	ftpPathName = conf.ftpKVPathNameR
        	svrDirName = conf.severDirName_daily
        elif argv[2].lower() == 'version':
        	buildIdFile = conf.kvVersionBuildIdFile
        	ftpPathName = conf.ftpVersionKVPathNameR
        	svrDirName = conf.severDirName_version
        elif argv[2].lower() == 'partial':
        	buildIdFile = conf.kvCustomBuildIdFile
        	ftpPathName = conf.ftpCustomKVPathNameR
        	svrDirName = conf.severDirName_partial
        debugPath = conf.kvdebug_path
        binPath = conf.kvbin_path
    	logPath = conf.kvlog_path
    	setupPath = conf.kvsetup_path
    if not (buildIdFile and ftpPathName and debugPath and binPath and logPath and setupPath):
    	print 'configuration error,please check conf.py'
    	return
    
    buildId=getBuildId(buildIdFile)
    currTime=time.strftime("%Y-%m-%d")
    filenames=os.listdir(setupPath)
    ftpDirName=svrDirName%(buildId)
    ftpPathDirName=ftpPathName+ftpDirName
    
    if not os.path.exists(ftpPathDirName):
        os.mkdir(ftpPathDirName)
    if not os.path.exists(ftpPathDirName+conf.ftpPathNameD):
        os.mkdir(ftpPathDirName+conf.ftpPathNameD)
    if not os.path.exists(ftpPathDirName+conf.ftpPathNameRR):
        os.mkdir(ftpPathDirName+conf.ftpPathNameRR)
    if not os.path.exists(ftpPathDirName+conf.ftpPathNameLog):
        os.mkdir(ftpPathDirName+conf.ftpPathNameLog)
    
    copyFiles(setupPath,conf.setupList,ftpPathDirName)
    copyFiles(debugPath,conf.binList,ftpPathDirName+conf.ftpPathNameD)
    copyFiles(binPath,conf.binList,ftpPathDirName+conf.ftpPathNameRR)
    copyFiles(logPath,conf.logList,ftpPathDirName+conf.ftpPathNameLog)

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
