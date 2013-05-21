# coding=UTF-8
"""
@author    thomas
@date    2013-03-07
@desc
    express build mode class library
"""

import sys,os,conf,xml.dom.minidom,datetime,comm
import rewrite_version,sign,fileop,send
import logging,time

build_step_creator = {
                      'prebuild':'PreBuild',
                      'locksvn':'LockSvn',
                      'svn':'Svn',
                      'rewriteversion':'RewriteVersion',
                      'build':'Build',
                      'pack':'Pack',
                      'sign':'Sign',
                      'verify':'Verify',
                      'install':'Install',
                      'signinstaller':'SignInstaller',
                      'verifyinstaller':'VerifyInstaller',
                      'send':'Send',
                      'symadd':'SymAdd',
                      'commit':'Commit',
                      'markupcode':'MarkupCode',
                      'releasesvn':'UnlockSvn',
                      'sendmail':'SendMail',
                      'postbuild':'PostBuild',
                      }
kvbuild_step_creator = {
                      'prebuild':'KVPreBuild',
                      'locksvn':'KVLockSvn',
                      'svn':'KVSvn',
                      'rewriteversion':'KVRewriteVersion',
                      'build':'KVBuild',
                      'pack':'KVPack',
                      'sign':'KVSign',
                      'verify':'KVVerify',
                      'install':'KVInstall',
                      'signinstaller':'KVSignInstaller',
                      'verifyinstaller':'KVVerifyInstaller',
                      'send':'KVSend',
                      'symadd':'KVSymAdd',
                      'commit':'KVCommit',
                      'markupcode':'KVMarkupCode',
                      'releasesvn':'KVUnlockSvn',
                      'sendmail':'KVSendMail',
                      'postbuild':'KVPostBuild',
                      }


#始终拿到所有项目名称-和buildswitch中的文件名匹配
def getSlns(product):
    checklogFile = ''
    if product == 'bdm':
        checklogFile = conf.checklog_file
    elif product == 'bdkv':
        checklogFile = conf.kvchecklog_file
    
    slns = []
    fileObj = open(checklogFile,'r')
    try:
        try:
            for line in fileObj.readlines():
                slns.append(line[0:line.find(' ')])
        finally:
            fileObj.close()
    except Exception,e:
        logging.error(e)
        logging.error(e)
    
    return slns
    
#得到svn锁定或解锁操作
def genSvnLockActions(product, action, value):
    #get svn lock/unlock settings
    actValue = False
    try:
        dom = xml.dom.minidom.parse(conf.svn_conf_file)
        root = dom.documentElement
        value = root.getAttribute(action)
        if value == 'true':
            actValue = True
        else:
            actValue = False
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    #noaction then return
    if not actValue:
        return []
    #gen lock/unlock actions for all compiled module and basic/stable
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/'+item+'.xml'
        try:
            dom = xml.dom.minidom.parse(confFile)
            root = dom.documentElement
            dir = root.getAttribute('dir')
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.getAttribute('build') != '1':#do not check force option
                    continue
                if node.getAttribute('product') != '' and node.getAttribute('product') != product:
                    continue
                commands.append(conf.sln_root + dir)
                break
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    commands.append(conf.sln_root + 'basic')
    commands.append(conf.sln_root + 'stable_proj')
    commands = list(set(commands))
    #already get all folders, now lock/unlock these folder
    cmd_details = []
    ecode = sys.getfilesystemencoding()
    for item in commands:
        infoFile = '..\\output\\svn\\' + item[item.rfind('\\')+1:] + '.info'
        command = 'svn list --non-interactive --no-auth-cache --username buildbot --password 123456 -R ' + item + ' > ' + infoFile
        os.system(command.encode(sys.getfilesystemencoding()))
        fh = open(infoFile)
        files = fh.readlines()
        fh.close()
        for f in files:
            f = f.strip(' \r\n')
            if f[-1] == '/' or f[-1] == '\\':
                continue
            if action == 'lock':
                cmd_details.append('svn lock --non-interactive --no-auth-cache --username buildbot --password 123456 --force ' + item + '/' + f.decode(ecode).encode('utf-8'))
            elif action == 'unlock':
                cmd_details.append('svn unlock --non-interactive --no-auth-cache --username buildbot --password 123456 --force ' + item + '/' + f.decode(ecode).encode('utf-8'))
    return cmd_details

    
#得到svn操作
def getSvnCommands(product, value):
    svnAction = 'update'
    if value == 2 or value == 4:
        svnAction = 'checkout'
    elif value == 1 or value == 3:
        svnAction = 'update'
    
    bForce = False
    if value == 1 or value == 2:
        bForce = True
    elif value == 3 or value == 4:
        bForce = False
        
    codeDir = ''
    revision = ''
    try:
        dom = xml.dom.minidom.parse(conf.svn_conf_file)
        root = dom.documentElement
        svnConfig = root.getAttribute('use')
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == svnConfig:
                if name == 'branch':
                    codeDir = '/branches/' + node.getAttribute('value')
                    revision = 'HEAD'
                elif name == 'tag':
                    codeDir = '/tags/' + node.getAttribute('value')
                    revision = 'HEAD'
                elif name == 'trunk':
                    codeDir = '/trunk'
                    revision = 'HEAD'
                elif name == 'revision':
                    codeDir = '/trunk'
                    revision = node.getAttribute('value')
                break
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    
    if revision == 'HEAD':
        revision = GetRemoteRevision()
    
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/'+item+'.xml'
        try:
            dom = xml.dom.minidom.parse(confFile)
            root = dom.documentElement
            dir = root.getAttribute('dir')
            svnDir = root.getAttribute('svnDir')
            if not svnDir:
                svnDir = dir + codeDir
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.getAttribute('build') != '1' and (not bForce):
                    continue
                if node.getAttribute('product') != '' and node.getAttribute('product') != product:
                    continue
                if svnAction == 'checkout':
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + svnDir + " " + conf.sln_root + dir
                elif svnAction == 'update':
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " "  + conf.sln_root + dir
                commands.append(command)
                break
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    if svnAction == 'update':
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " "  + conf.sln_root + "basic")
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " "  + conf.sln_root + "stable_proj")
    elif svnAction == 'checkout':
        commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "basic_proj" + codeDir + " " + conf.sln_root + "basic")
        commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "stable_proj" + codeDir + " " + conf.sln_root + "stable_proj")
    commands = list(set(commands))
    return commands

def GetRemoteRevision():
    f = open(conf.svn_remote_info_file)
    svn_info_lines = f.readlines()
    f.close()
    revision = ''
    for line in svn_info_lines:
        index = line.find(': ')
        if index != -1:
            secondPart = line[index+2:]
            secondPart = secondPart.strip(' \r\n')
            bFit = True
            for i in secondPart:
                if i < '0' or i > '9':
                    bFit = False
                    break
            if bFit:
                revision = secondPart
                break
    if revision == '':
        return 'HEAD'
    else:
        return revision

def ExpendMarkupValue(product, str, code_revision, codeDir):
    #替换$revision、$version等
    f = open(conf.svn_remote_info_file)
    svn_info_lines = f.readlines()
    f.close()
    revision = ''
    version = ''
    if code_revision == '':
        for line in svn_info_lines:
            index = line.find(': ')
            if index != -1:
                secondPart = line[index+2:]
                secondPart = secondPart.strip(' \r\n')
                bFit = True
                for i in secondPart:
                    if i < '0' or i > '9':
                        bFit = False
                        break
                if bFit:
                    revision = secondPart
                    break
    else:
        revision = code_revision
    
    local_version_file = ''
    
    if code_revision == '':
        if product == 'bdm':
            local_version_file = conf.bdm_nsifile_daily
        elif product == 'bdkv':
            local_version_file = conf.bdkv_nsifile_daily
    if code_revision != '' or (not os.path.exists(local_version_file)):
        remote_version_folder = ''
        local_version_folder = ''
        local_version_file = '../output/svn/product_version.info'
        if product == 'bdm':
            remote_version_folder = conf.svn_url + 'basic_proj' + codeDir + '/Tools/SetupScript'
            local_version_folder = '..\\output\\svn\\SetupScript'
            local_version_file = '../output/svn/SetupScript/BDM_setup.nsi'
        elif product == 'bdkv':
            remote_version_folder = conf.svn_url + 'basic_proj' + codeDir + '/Tools/KVSetupScript'
            local_version_folder = '..\\output\\svn\\KVSetupScript'
            local_version_file = '../output/svn/KVSetupScript/BDKV_setup.nsi'
        command = 'rd /Q /S ' + local_version_folder
        os.system(command)
        command = 'svn checkout --non-interactive --no-auth-cache --username buildbot --password 123456 --revision ' + revision + ' ' + remote_version_folder + ' ' + local_version_folder
        os.system(command)
    f = open(local_version_file)
    version_lines = f.readlines()
    f.close()
    for line in version_lines:
        index = line.find('!define RELEASE_VERSION  ')
        if index != -1:
            secondPart = line[index+25:]
            version = secondPart.strip('" \r\n')
            if code_revision != '':
                try:
                    version = '%d' % (int(version) + 1)
                except Exception,e:
                    print e
            break
    if revision == '' or version == '':
        return (str,revision)
    else:
        str = str.replace('$r', 'r'+revision)
        str = str.replace('$v', 'v'+version)
        tst = '%f' % time.time()
        str = str.replace('$t', 't'+tst)
        return (str,revision)

def getMarkupCodeCommands(product,value):
    #codebase must be considered
    codeDir = ''
    revision = ''
    code_revision = ''
    try:
        dom = xml.dom.minidom.parse(conf.svn_conf_file)
        root = dom.documentElement
        svnConfig = root.getAttribute('use')
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == svnConfig:
                if name == 'branch':
                    codeDir = '/branches/' + node.getAttribute('value')
                elif name == 'tag':
                    codeDir = '/tags/' + node.getAttribute('value')
                elif name == 'trunk':
                    codeDir = '/trunk'
                elif name == 'revision':
                    codeDir = '/trunk'
                    code_revision = node.getAttribute('value')
                break
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    
    #markup info
    markupType = ''
    markupValue = ''
    try:
        dom = xml.dom.minidom.parse(conf.markup_conf_file)
        root = dom.documentElement
        markupType = root.getAttribute('use')
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == markupType:
                markupValue = node.getAttribute('value')
                break
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    
    #svn commands
    if markupType == '' or markupValue == '' or markupType == 'none':
        return []
    else:
        actType = markupType
        (markupValue,revision) = ExpendMarkupValue(product, markupValue, code_revision, codeDir)
        if markupType == '+branch' or markupType == '-branch':
            markupType = '/branches/'
        elif markupType == '+tag' or markupType == '-tag':
            markupType = '/tags/'
        commands = []
        if actType[0] == '+':
            msg = 'bypbuild copy %s' % datetime.datetime.now()
        elif actType[0] == '-':
            msg = 'bypbuild delete %s' % datetime.datetime.now()
        slns = getSlns(product)
        for item in slns:
            confFile = './BuildSwitch/'+item+'.xml'
            try:
                dom = xml.dom.minidom.parse(confFile)
                root = dom.documentElement
                dir = root.getAttribute('dir')
                svnDir = root.getAttribute('svnDir')
                if not svnDir:
                    svnDir = dir + codeDir
                if actType[0] == '+':
                    command = "svn copy --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + svnDir + " " + conf.svn_url + dir + markupType + markupValue + ' -m "' + msg + '"'
                elif actType[0] == '-':
                    command = "svn delete " + conf.svn_url + dir + markupType + markupValue + ' -m "' + msg + '"'
                commands.append(command)
            except Exception,e:
                logging.error("error occers when parsing xml or run command:")
                logging.error(e)
        #add basic and stable
        if actType[0] == '+':
            commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "basic_proj" + codeDir + " " + conf.svn_url + "basic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "stable_proj" + codeDir + " " + conf.svn_url + "stable_proj" + markupType + markupValue + ' -m "' + msg + '"')
        elif actType[0] == '-':
            commands.append("svn delete " + conf.svn_url + "basic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            commands.append("svn delete " + conf.svn_url + "stable_proj" + markupType + markupValue + ' -m "' + msg + '"')
        commands = list(set(commands))
        return commands
    
def getBuildCommands(product,value):
    checklogFile = ''
    errDir = ''
    if product == 'bdm':
        checklogFile = conf.checklog_file
        errDir = conf.log_path
    elif product == 'bdkv':
        checklogFile = conf.kvchecklog_file
        errDir = conf.kvlog_path

    vcbuildAction = ''
    if value == 3 or value == 4:
        vcbuildAction = '/rebuild'
    elif value == 1 or value == 2:
        vcbuildAction = '/rebuild'#always rebuild
    
    bForce = False
    if value == 1 or value == 3:
        bForce = True
    elif value == 2 or value == 4:
        bForce = False
    
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/'+item+'.xml'
        try:
            dom = xml.dom.minidom.parse(confFile)
            root = dom.documentElement
            dir = root.getAttribute('dir')
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.getAttribute('build') != '1' and (not bForce):
                    continue
                if node.getAttribute('product') != '' and node.getAttribute('product') != product:
                    continue
                type = node.getAttribute('type')
                logName = ''
                if type.lower().find('release') != -1:
                    logName = 'Release'
                elif type.lower().find('debug') != -1:
                    logName = 'Debug'
                else:
                    continue
                command = "vcbuild " + vcbuildAction + " /time /M1 /errfile:" + errDir + item + logName + ".log " + conf.sln_root \
                 + dir + "\\Projects\\" + item + ".sln \"" + type + "\""
                commands.append(command)
            writer = open(confFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    return commands
    
    
def getInstallOptions():
    pkgFile = './BuildSwitch/Package.xml'
    try:
        dom = xml.dom.minidom.parse(pkgFile)
        root = dom.documentElement
        bInstall = False if root.getAttribute('install') == '0' else True
        bInstallFull = False if root.getAttribute('install_full') == '0' else True
        bInstallUpdate = False if root.getAttribute('install_update') == '0' else True
        return (bInstall,bInstallFull,bInstallUpdate)
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
        
def getViruslibVersion():
    vlibVersionFile = conf.sln_root + 'basic\\KVOutput\\binrelease\\kav\\bases\\u0607g.xml'
    try:
        f = open(vlibVersionFile)
        buf = f.read()
        f.close()
        iIndex = buf.find('UpdateDate')
        if iIndex == -1:
            return ''
        vStr = buf[iIndex + 12:iIndex + 25]
        try:
            vRet = vStr[4:8] + vStr[2:4] + vStr[0:2] + vStr[8:]
            return vRet
        except:
            return ''
    except Exception,e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)

def installKvFullPackage():
    #prepare
    command = 'copy /Y ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    os.system(command.encode(sys.getfilesystemencoding()))
    setupFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    file_r = open(setupFile)
    lines = file_r.readlines()
    file_r.close()
    for index in range(len(lines)):
        if lines[index].find('OutFile')!= -1:
            lines[index] = 'OutFile "..\kvsetup\Baidusd_Setup_Full_${BUILD_BASELINE}.exe"\r\n'
    file_w  = open(setupFile,"w")
    file_w .writelines(lines)
    file_w .close()
    
    command = 'rd /Q /S ..\\output\\backup\\bases\\'
    os.system(command)
    command = 'xcopy /Y /E /S ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases ..\output\\backup\\bases\\'
    os.system(command)
    command = 'rd /Q /S ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases'
    os.system(command)
    command = 'xcopy /Y /E /S ' + conf.sln_root + 'basic\\kvoutput\\bases ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases\\'
    os.system(command)
    
    command = 'copy /Y ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_Language.nsh ..\\output\\backup\\KV_Language.nsh'
    os.system(command.encode(sys.getfilesystemencoding()))
    vlibVersion = getViruslibVersion()
    if vlibVersion != '':
        vInstallFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_Language.nsh'
        file_r = open(vInstallFile)
        lines = file_r.readlines()
        file_r.close()
        for index in range(len(lines)):
            if lines[index].find('MACRO_ANTIVIRUS_UPDATETIME')!= -1:
                lines[index] = '!define MACRO_ANTIVIRUS_UPDATETIME      "%s"\r\n' % vlibVersion
        file_w  = open(vInstallFile,"w")
        file_w .writelines(lines)
        file_w .close()
    
    #install
    command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    os.system(command.encode(sys.getfilesystemencoding()))
    #clean
    command = 'del /Q /S ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    os.system(command)
    command = 'copy /Y ..\\output\\backup\\KV_Language.nsh ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_Language.nsh'
    os.system(command)
    command = 'del /Q /S ..\\output\\backup\\KV_Language.nsh'
    os.system(command)
    command = 'rd /Q /S ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases'
    os.system(command)
    command = 'xcopy /Y /E /S ..\\output\\backup\\bases ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases\\'
    os.system(command)
    command = 'rd /Q /S ..\\output\\backup\\bases'
    os.system(command)

def updatePackage(product):
    buildlineFile = ''
    buildline = 0
    buildType = 'daily'
    if product == 'bdm':
        buildlineFile = conf.sln_root + 'basic\\Tools\\SetupScript\\include\\buildline.nsi'
    elif product == 'bdkv':
        buildlineFile = conf.sln_root + 'basic\\Tools\\KVSetupScript\\include\\buildline.nsi'
    ctx = comm.getMsg(buildlineFile)
    if ctx.find('0') != -1:
        buildType = 'daily'
    elif ctx.find('1') != -1:
        builtType = 'version'
    rewrite_version.main(3,['rewrite_version.py',product,buildType])
    

def makeBinplace(product,files,buildtype):
    if product == 'bdm':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\Output\\Symbols\\' + buildtype + '\\Full -r ' + conf.sln_root + 'basic\\Output\\Symbols\\' + buildtype + '\\ -:DEST BDM ' + conf.sln_root + files
    elif product == 'bdkv':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\' + buildtype + '\\Full -r ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\' + buildtype + '\\ -:DEST BDKV ' + conf.sln_root + files

def genSymbols(product):
    commands = []
    if product == 'bdm':
        #release
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\*.exe','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\bdmantivirus\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\FTSOManager\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\FTSWManager\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmkvscanplugin\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmhomepageplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmmainframeplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmsomanagerplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmswmanagerplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\bdmtrayplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinRelease\\plugins\\rtpplugins\\*.dll','Release'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Full\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Stripped\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
        #debug
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\*.exe','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\bdmantivirus\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\FTSOManager\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\FTSWManager\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmkvscanplugin\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmhomepageplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmmainframeplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmsomanagerplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmswmanagerplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\bdmtrayplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdm','basic\\Output\\BinDebug\\plugins\\rtpplugins\\*.dll','Debug'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Debug\\Full\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Debug /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Debug\\Stripped\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Debug /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Debug\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Debug /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Debug\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Debug /t "THIRD"')
    elif product == 'bdkv':
        #release
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.exe','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\bdmantivirus\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\bdmsysrepair\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\drivers\\*.sys','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\bdkv\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll','Release'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll','Release'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Full\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Stripped\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
        #debug
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\*.exe','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\bdmantivirus\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\bdmsysrepair\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\drivers\\*.sys','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\plugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\plugins\\bdkv\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\plugins\\bdkvtrayplugins\\*.dll','Debug'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinDebug\\plugins\\bdkvrtpplugins\\*.dll','Debug'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Debug\\Full\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Debug /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Debug\\Stripped\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Debug /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Debug\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Debug /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Debug\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Debug /t "THIRD"')
    return commands

def genPrebuildActions(product,value):
    commands = []
    if value == 1 or value == 2:
        commands.append('del /Q ' + conf.sln_root + 'basic\\include\\CommonInclude\\BDMVersion.h')
        commands.append('del /Q ' + conf.sln_root + 'basic\\include\\CommonInclude\\BuildVer.h')
        if product == 'bdm':
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\buildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\versionbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\SetupScript\\include\\buildline.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\setup\\*.exe')
            commands.append('del /Q ..\\output\\setup\\*.exe')
            commands.append('del /Q ..\\output\\err\\*.log')
        elif product == 'bdkv':
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvversionbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\buildline.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\kvsetup\\*.exe')
            commands.append('del /Q ..\\output\\kvsetup\\*.exe')
            commands.append('del /Q ..\\output\\kverr\\*.log')
    if value == 2:
        commands.append('del /Q /S ' + conf.sln_root + 'basic\\lib')
        if product == 'bdm':
            commands.append('del /Q /S ' + conf.sln_root + 'basic\\Output')
        elif product == 'bdkv':
            commands.append('del /Q /S ' + conf.sln_root + 'basic\\KVOutput')
    commands.append('svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD ' + conf.sln_root + 'basic')
    return commands

##############################################

class BuildStep:
    g_t_weight = 0
    g_c_weight = 0
    def __init__(self,n,v,o,w,p):
        self.name = n
        self.value = v
        self.order = o
        self.weight = w
        self.cweight = 0
        self.para = p
    
    def __str__(self):
        #return 'name=%s value=%s order=%d' % (self.name,self.value,self.order)
        pass
    
    def act(self):
        self.update_step(0, bFinish = True)
    
    def report(self, msrc, msg):
        if len(self.para) == 0:
            logging.info(msg)
        elif self.para[0] == 'wk-build-log':
            sid = self.para[1]
            ws = self.para[2]
            #整饰特殊字符
            msg = msg.replace('\\','/')
            msg = msg.replace('"',' ')
            msg = msg.replace('\'',' ')
            msg = msg.replace('\r',' ')
            msg = msg.replace('\n',' ')
            content = '{"msrc":"%s","content":"%s"}' % (msrc, msg)
            logging.info('send message from worker, sid:%s, message:%s' % (sid,content))
            ws.send(content)
    
    def update_step(self, w, bFinish = False):
        if self.cweight == self.weight:
            pass
        elif self.cweight + w >= self.weight or bFinish:
            BuildStep.g_c_weight += self.weight - self.cweight
            self.cweight = self.weight
            percentage = float(BuildStep.g_c_weight) / float(BuildStep.g_t_weight) * 100
            msg = '%d' % percentage
            logging.info('cweight : %d, weight : %d, g_c_weight : %d, g_t_weight : %d, w : %d',self.cweight, self.weight, BuildStep.g_c_weight, BuildStep.g_t_weight, w)
            self.report('wk-build-progress',msg)
        else:
            BuildStep.g_c_weight += w
            self.cweight += w
            percentage = float(BuildStep.g_c_weight) / float(BuildStep.g_t_weight) * 100
            msg = '%d' % percentage
            logging.info('cweight : %d, weight : %d, g_c_weight : %d, g_t_weight : %d, w : %d',self.cweight, self.weight, BuildStep.g_c_weight, BuildStep.g_t_weight, w)
            self.report('wk-build-progress',msg)

##############################################
# 0

class PreBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM prebuild operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genPrebuildActions('bdm',self.value)
            for item in commands:
                self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
                self.update_step(1)
        BuildStep.act(self)
    
class KVPreBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV prebuild operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genPrebuildActions('bdkv',self.value)
            for item in commands:
                self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
                self.update_step(1)
        BuildStep.act(self)
            
##############################################
# 0,1,2,3,4

class Svn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM svn operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            command = 'svn info --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.svn_url + ' > ' + conf.svn_remote_info_file
            os.system(command)
            commands = getSvnCommands('bdm',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No svn commands')
            else:
                for item in commands:
                    if item.find('checkout') != -1:
                        subdir = item[item.find(conf.svn_url) + len(conf.svn_url):]
                        subdir = subdir[0:subdir.find('/')]
                        if subdir.lower() == 'basic_proj':
                            subdir = 'basic'
                        command = 'rd /Q /S ..\\..\\' + subdir
                        self.report('wk-build-log', command)
                        os.system(command.encode(sys.getfilesystemencoding()))
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    else:
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    self.update_step(3)
        BuildStep.act(self)
    
class KVSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV svn operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            command = 'svn info --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.svn_url + ' > ' + conf.svn_remote_info_file
            os.system(command)
            commands = getSvnCommands('bdkv',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No svn commands')
            else:
                for item in commands:
                    if item.find('checkout') != -1:
                        subdir = item[item.find(conf.svn_url) + len(conf.svn_url):]
                        subdir = subdir[0:subdir.find('/')]
                        if subdir.lower() == 'basic_proj':
                            subdir = 'basic'
                        command = 'rd /Q /S ..\\..\\' + subdir
                        self.report('wk-build-log', command)
                        os.system(command.encode(sys.getfilesystemencoding()))
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    else:
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    self.update_step(3)
        BuildStep.act(self)
    
##############################################
# 0,1

class LockSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM lock svn operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genSvnLockActions('bdm','lock',self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVLockSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV lock svn operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genSvnLockActions('bdkv','lock',self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
##############################################
# 0,1,2

class RewriteVersion(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM update build version and resource definition"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'python rewrite_version.py bdm daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdm','daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdm version'
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdm','version'])
        BuildStep.act(self)

    
class KVRewriteVersion(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV update build version and resource definition"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'python rewrite_version.py bdkv daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdkv','daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdkv version'
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdkv','version'])
        BuildStep.act(self)
    
##############################################
# 0,1,2

class Build(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM compiling and building"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            commands = getBuildCommands('bdm',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No build commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item)
                    self.update_step(10)
                    os.system(item.encode(sys.getfilesystemencoding()))
            BuildStep.act(self)
            bErr = False
            for file in os.listdir(conf.log_path):
                if file[-3:] == 'log':
                    errLog = comm.getMsg(conf.log_path + file)
                    if errLog != '' and errLog.find('error PRJ0002') != -1 and errLog.find('Error result 31 returned from') != -1 and errLog.find('mt.exe') != -1:#just be careful
                        self.report('wk-build-log','<h5>PRJ0002 error found, try rebuilding specific solution<h5>')
                        self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                        bReCompiler = False
                        for item in commands:
                            if item.find(conf.log_path + file) != -1:
                                bRecompiler = True
                                self.report('wk-build-log', item)
                                os.system(item.encode(sys.getfilesystemencoding()))
                                errLog = comm.getMsg(conf.log_path + file)
                                break
                        if not bReCompiler:
                            os.system('del /Q ' + conf.log_path + file)
                            errLog = ''
                    if errLog != '':
                        bErr = True
                        break
            if bErr:
                #check whether compiler error is ignored
                bIgnoreFault = False
                miscFile = './buildswitch/Misc.xml'
                try:
                    dom = xml.dom.minidom.parse(miscFile)
                    root = dom.documentElement
                    for node in root.childNodes:
                        if node.nodeType != node.ELEMENT_NODE:
                            continue
                        name = node.getAttribute('name')
                        if name == 'ignorefault' and node.getAttribute('value') == '1':
                            bIgnoreFault = True
                            break
                except Exception,e:
                    logging.error("error occers when parsing xml or run command:")
                    logging.error(e)
                if bIgnoreFault:
                    msg = '<h5>Build error(s) found, xbuild continues, please handler these error(s) below later : </h5>'
                    self.report('wk-build-log',msg)
                else:
                    msg = '<h5>Build error(s) found, xbuild quit, please handler these error(s) below : </h5>'
                    self.report('wk-status-change', 'error')
                    self.report('wk-build-log',msg)
                for file in os.listdir(conf.log_path):
                    if file[-3:] == 'log':
                        errLog = comm.getMsg(conf.log_path + file)
                        if errLog != '':
                            self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                            self.report('wk-build-log','<h5>' + file + '</h5>')
                            fp = open(conf.log_path + file)
                            lines = fp.readlines()
                            fp.close()
                            for line in lines:
                                self.report('wk-build-log',line)
                self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                if not bIgnoreFault:
                    raise Exception(msg)
        BuildStep.act(self)
    
class KVBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV compiling and building"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            commands = getBuildCommands('bdkv',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No build commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item)
                    self.update_step(10)
                    os.system(item.encode(sys.getfilesystemencoding()))
            BuildStep.act(self)
            bErr = False
            for file in os.listdir(conf.kvlog_path):
                if file[-3:] == 'log':
                    errLog = comm.getMsg(conf.kvlog_path + file)
                    if errLog != '' and errLog.find('error PRJ0002') != -1 and errLog.find('Error result 31 returned from') != -1 and errLog.find('mt.exe') != -1:#just be careful
                        self.report('wk-build-log','<h5>PRJ0002 error found, try rebuilding specific solution<h5>')
                        self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                        bReCompiler = False
                        for item in commands:
                            if item.find(conf.kvlog_path + file) != -1:
                                bReCompiler = True
                                self.report('wk-build-log', item)
                                os.system(item.encode(sys.getfilesystemencoding()))
                                errLog = comm.getMsg(conf.kvlog_path + file)
                                break
                        if not bReCompiler:
                            os.system('del /Q ' + conf.kvlog_path + file)
                            errLog = ''
                    if errLog != '':
                        bErr = True
                        break
            if bErr:
                #check whether compiler error is ignored
                bIgnoreFault = False
                miscFile = './buildswitch/Misc.xml'
                try:
                    dom = xml.dom.minidom.parse(miscFile)
                    root = dom.documentElement
                    for node in root.childNodes:
                        if node.nodeType != node.ELEMENT_NODE:
                            continue
                        name = node.getAttribute('name')
                        if name == 'ignorefault' and node.getAttribute('value') == '1':
                            bIgnoreFault = True
                            break
                except Exception,e:
                    logging.error("error occers when parsing xml or run command:")
                    logging.error(e)
                if bIgnoreFault:
                    msg = '<h5>Build error(s) found, xbuild continues, please handler these error(s) below later : </h5>'
                    self.report('wk-build-log',msg)
                else:
                    msg = '<h5>Build error(s) found, xbuild quit, please handler these error(s) below : </h5>'
                    self.report('wk-status-change', 'error')
                    self.report('wk-build-log',msg)
                for file in os.listdir(conf.kvlog_path):
                    if file[-3:] == 'log':
                        errLog = comm.getMsg(conf.kvlog_path + file)
                        if errLog != '':
                            self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                            self.report('wk-build-log','<h5>' + file + '</h5>')
                            fp = open(conf.kvlog_path + file)
                            lines = fp.readlines()
                            fp.close()
                            for line in lines:
                                self.report('wk-build-log',line)
                self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                if not bIgnoreFault:
                    raise Exception(msg)
        BuildStep.act(self)
    
##############################################
# 0,1

class Pack(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM packing resources"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'cscript pack.vbs bdm'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVPack(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV packing resources"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'cscript pack.vbs bdkv'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
##############################################
# 0,1

class Sign(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM signning files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'python fileop.py kvsign ' + conf.sln_root + 'basic\\Output\\BinDebug\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign',conf.sln_root + 'basic\\Output\\BinDebug\\','*.exe'])
            command = 'python fileop.py kvsign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign',conf.sln_root + 'basic\\Output\\BinRelease\\','*.exe'])

            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\Output\\BinDebug\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign_kav',conf.sln_root + 'basic\\Output\\BinDebug\\','*.exe'])
            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign_kav',conf.sln_root + 'basic\\Output\\BinRelease\\','*.exe'])

            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Output\\BinRelease\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdm',conf.sln_root + 'basic\\Output\\BinRelease\\'])
            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'
            self.report('wk-build-log',command)
            sign.main(3,['sign.py','bdm',conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'])
        BuildStep.act(self)
    
class KVSign(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV signning files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'python fileop.py kvsign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            self.update_step(14)
            
            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign_kav',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            self.update_step(14)
            
            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdkv',conf.sln_root + 'basic\\KVOutput\\BinRelease\\'])
            self.update_step(14)

            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdkv',conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'])
            self.update_step(30)

        BuildStep.act(self)
    
##############################################
# 0,1

class Verify(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM verifing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            os.system('del /Q ' + conf.verify_log_file.encode(sys.getfilesystemencoding()))
            commands = []
            commands.append('python fileop.py verify_file_exist ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.*')
            commands.append('python fileop.py verify_file_version ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py verify_baidu_sign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            for item in commands:
                self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','verify_file_exist',conf.sln_root + 'basic\\Output\\BinRelease\\','*.*'])
            fileop.main(4,['fileop.py','verify_file_version',conf.sln_root + 'basic\\Output\\BinRelease\\','*.exe,*.dll,*.sys'])
            fileop.main(4,['fileop.py','verify_baidu_sign',conf.sln_root + 'basic\\Output\\BinRelease\\','*.exe,*.dll,*.sys'])
        BuildStep.act(self)
    
class KVVerify(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV verifing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            os.system('del /Q ' + conf.kvverify_log_file.encode(sys.getfilesystemencoding()))
            commands = []
            commands.append('python fileop.py kvverify_file_exist ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.*')
            commands.append('python fileop.py kvverify_file_version ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py kvverify_driver_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ .exe,*.dll,*.sys')
            for item in commands:
                self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvverify_file_exist',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.*'])
            fileop.main(4,['fileop.py','kvverify_file_version',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','.exe,*.dll,*.sys'])
            fileop.main(4,['fileop.py','kvverify_driver_sign',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_kav_sign',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_baidu_sign',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe,*.dll,*.sys'])
        BuildStep.act(self)

##############################################
# 0,1

class Install(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM building installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            (bInstall, bInstallFull, bInstallUpdate) = getInstallOptions()
            if bInstall:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
                self.report('wk-build-log', command)
                os.system(command.encode(sys.getfilesystemencoding()))
            if bInstall and bInstallUpdate:
                updatePackage('bdm')
                if bInstall:
                    command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
                    self.report('wk-build-log', command)
                    os.system(command.encode(sys.getfilesystemencoding()))
            bOk = False
            for file in os.listdir(conf.original_setup_path):
                if file[-3:] == 'exe':
                    bOk = True
                    break
            if not bOk:
                msg = 'failed to build installer, please check nsis script files'
                self.report('wk-build-log','------------------------------------------------------')
                self.report('wk-build-log','<h5>'+msg+'</h5>')
                raise Exception(msg)
            command = 'xcopy /Y ' + conf.original_setup_path.replace('/','\\') + '*.exe ' + conf.setup_path.replace('/','\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVInstall(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV building installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            (bInstall, bInstallFull, bInstallUpdate) = getInstallOptions()
            if bInstall:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
                self.report('wk-build-log', command)
                os.system(command.encode(sys.getfilesystemencoding()))
            if bInstallFull:
                installKvFullPackage()
            if (bInstall or bInstallFull) and bInstallUpdate:
                updatePackage('bdkv')
                if bInstall:
                    command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
                    self.report('wk-build-log', command)
                    os.system(command.encode(sys.getfilesystemencoding()))
                if bInstallFull:
                    installKvFullPackage()
            #check exe
            bOk = False
            for file in os.listdir(conf.original_kvsetup_path):
                if file[-3:] == 'exe':
                    bOk = True
                    break
            if not bOk:
                msg = 'failed to build installer, please check nsis script files'
                self.report('wk-build-log','------------------------------------------------------')
                self.report('wk-build-log','<h5>'+msg+'</h5>')
                raise Exception(msg)
            
            #copy exe
            command = 'xcopy /Y ' + conf.original_kvsetup_path.replace('/','\\') + '*.exe ' + conf.kvsetup_path.replace('/','\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
##############################################
# 0,1

class SignInstaller(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM signning installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'xcopy /Y ' + conf.original_setup_path.replace('/','\\') + '*.exe ' + conf.setup_path.replace('/','\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(1)

            command = 'python fileop.py sign ..\\output\\setup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign','..\\output\\setup\\','*.exe'])
            self.update_step(1)
            
            command = 'python fileop.py kvsign_kav ..\\output\\setup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign_kav','..\\output\\setup\\','*.exe'])
            self.update_step(1)

            command = 'python sign.py bdm ..\\output\\setup\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdm','..\\output\\setup\\'])
        BuildStep.act(self)
    
class KVSignInstaller(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV signning installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'xcopy /Y ' + conf.original_kvsetup_path.replace('/','\\') + '*.exe ' + conf.kvsetup_path.replace('/','\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(1)

            command = 'python fileop.py sign ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign','..\\output\\kvsetup\\','*.exe'])
            self.update_step(1)
            
            command = 'python fileop.py kvsign_kav ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign_kav','..\\output\\kvsetup\\','*.exe'])
            self.update_step(1)
            
            command = 'python sign.py bdkv ..\\output\\kvsetup\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdkv','..\\output\\kvsetup\\'])
            self.update_step(1)
        BuildStep.act(self)
    
##############################################
# 0,1

class VerifyInstaller(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM verifing installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py verify_file_version ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py verify_baidu_sign ..\\output\\setup\\ *.exe')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4,['fileop.py','verify_file_version','..\\output\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','verify_baidu_sign','..\\output\\setup\\','*.exe'])
        BuildStep.act(self)
    
class KVVerifyInstaller(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV verifing installer"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py kvverify_file_version ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_driver_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ..\\output\\setup\\ *.exe')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4,['fileop.py','kvverify_file_version','..\\output\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_driver_sign','..\\output\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_kav_sign','..\\output\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_baidu_sign','..\\output\\setup\\','*.exe'])
        BuildStep.act(self)

##############################################
# 0,1

class Send(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM sending files to archive folder"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdm daily')
            for item in commands:
                self.report('wk-build-log', item)
            send.main(3,['send.py','bdm','daily'])
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdm version')
            for item in commands:
                self.report('wk-build-log', item)
            send.main(3,['send.py','bdm','version'])
        BuildStep.act(self)
    
class KVSend(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV sending files to archive folder"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdkv daily')
            for item in commands:
                self.report('wk-build-log', item)
            send.main(3,['send.py','bdkv','daily'])
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdkv version')
            for item in commands:
                self.report('wk-build-log', item)
            send.main(3,['send.py','bdkv','version'])
        BuildStep.act(self)
    
##############################################
# 0,1

class SymAdd(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM collecting symbols to symbol server"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = genSymbols('bdm')
            for item in commands:
                self.report('wk-build-log', item)
                self.update_step(1)
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVSymAdd(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV collecting symbols to symbol server"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            commands = genSymbols('bdkv')
            for item in commands:
                self.report('wk-build-log', item)
                self.update_step(1)
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
##############################################
# 0,1

class Commit(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM committing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'svn update --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.sln_root + 'basic --accept mine-full'
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(5)
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command.replace('123456','XXXXXX'))
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(10)
        BuildStep.act(self)
    
class KVCommit(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV committing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            command = 'svn update --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.sln_root + 'basic --accept mine-full'
            self.report('wk-build-log', command.replace('123456','XXXXXX'))
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(5)
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit --non-interactive --no-auth-cache --username buildbot --password 123456 ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command.replace('123456','XXXXXX'))
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(10)
        BuildStep.act(self)
    
##############################################
# 0,1,2
class MarkupCode(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM markup code operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            commands = getMarkupCodeCommands('bdm',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No markup code commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item.replace('123456','XXXXXX'))
                    os.system(item.encode(sys.getfilesystemencoding()))
                    self.update_step(1)
        BuildStep.act(self)
    
class KVMarkupCode(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV markup code operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        else:
            commands = getMarkupCodeCommands('bdkv',self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No markup code commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item.replace('123456','XXXXXX'))
                    os.system(item.encode(sys.getfilesystemencoding()))
                    self.update_step(1)
        BuildStep.act(self)

##############################################
# 0,1

class UnlockSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM unlock svn operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genSvnLockActions('bdm','unlock',self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVUnlockSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV unlock svn operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            commands = genSvnLockActions('bdkv','unlock',self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('123456','XXXXXX'))
                os.system(item.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
        
##############################################
# 0,1

class SendMail(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM send notification mail"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            pass
        BuildStep.act(self)
    
class KVSendMail(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV send notification mail"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            pass
        BuildStep.act(self)
        
##############################################
# 0,1

class PostBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM postbuild operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            self.report('wk-build-log', 'Cleanning...')
        BuildStep.act(self)
    
class KVPostBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV postbuild operations"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            self.report('wk-build-log', 'Cleanning...')
        BuildStep.act(self)
    
##############################################
