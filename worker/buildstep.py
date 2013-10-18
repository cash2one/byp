# coding=UTF-8
"""
@author    thomas
@date    2013-03-07
@desc
    express build mode class library
"""

import sys, os, conf, xml.dom.minidom, datetime, comm
import rewrite_version, sign, fileop, rcgen, send
import logging, time
import random

build_step_creator = {
                      'prebuild':'PreBuild',
                      'locksvn':'LockSvn',
                      'svn':'Svn',
                      'rewriteversion':'RewriteVersion',
                      'rcgen':'Rcgen',
                      'build':'Build',
                      'pack':'Pack',
                      'rebase':'Rebase',
                      'sign':'Sign',
                      'verify':'Verify',
                      'install':'Install',
                      'signinstaller':'SignInstaller',
                      'installermd5':'CalcInstallerMd5',
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
                      'rcgen':'KVRcgen',
                      'build':'KVBuild',
                      'pack':'KVPack',
                      'rebase':'KVRebase',
                      'sign':'KVSign',
                      'verify':'KVVerify',
                      'install':'KVInstall',
                      'signinstaller':'KVSignInstaller',
                      'installermd5':'KVCalcInstallerMd5',
                      'verifyinstaller':'KVVerifyInstaller',
                      'send':'KVSend',
                      'symadd':'KVSymAdd',
                      'commit':'KVCommit',
                      'markupcode':'KVMarkupCode',
                      'releasesvn':'KVUnlockSvn',
                      'sendmail':'KVSendMail',
                      'postbuild':'KVPostBuild',
                      }

def randomVersion():
    return '1.0.%d.%d' % (random.randint(0,1000), random.randint(0,1000))
    
def finalBuildpackage(product, type, buildcmd, nsiFile):
    bMashupInstaller = False
    bMashupVersion = False
    try:
        dom = xml.dom.minidom.parse('./BuildSwitch/Misc.xml')
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'mashup_installer':
                val = node.getAttribute('value')
                if val == '1':
                    bMashupInstaller = True
            elif name == 'mashup_version':
                val = node.getAttribute('value')
                if val == '1':
                    bMashupVersion = True
    except Exception, e:
        logging.error("error occers when parsing xml : misc.xml")
        logging.error(e)
    
    icoFile = ''
    if product == 'bdkv':
        if type == 'mini':
            icoFile = sln_root + 'basic\\tools\\KVNetInstall\\res\\setup.ico'
        elif type == 'normal':
            icoFile = sln_root + 'basic\\tools\\KVSetupScript\\res\\setup.ico'
        elif type == 'full':
            icoFile = sln_root + 'basic\\tools\\KVSetupScript\\res\\setup.ico'
    elif product == 'bdm':
        if type == 'mini':
            icoFile = sln_root + 'basic\\tools\\BDMNetInstall\\res\\setup.ico'
        elif type == 'normal':
            icoFile = sln_root + 'basic\\tools\\SetupScript\\res\\setup.ico'
        elif type == 'full':
            icoFile = sln_root + 'basic\\tools\\SetupScript\\res\\setup.ico'
    if icoFile != '' and bMashupInstaller:
        command = 'copy /Y ' + icoFile + ' ' + icoFile + '.bk'
        os.system(command)
        command = conf.byp_bin_path + 'modifyICO.exe ' + icoFile + ' ' + icoFile
        os.system(command)
        
    if bMashupVersion:
        file_r = open(nsiFile)
        lines = file_r.readlines()
        file_r.close()
        installerFullName = comm.getInstallerFullName(product)
        installerVersion = comm.getInstallerVersion(product)
        for index in range(len(lines)):
            if lines[index].find('OutFile') != -1:
                    lines[index] = lines[index].replace(installerVersion,randomVersion())
            if lines[index].find('VIProductVersion') != -1:
                lines[index] = 'VIProductVersion "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "FileVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "ProductVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"\r\n' % installerVersion
        file_w = open(nsiFile, "w")
        file_w .writelines(lines)
        file_w .close()
    
    #build package
    os.system(buildcmd.encode(sys.getfilesystemencoding()))
    
    if icoFile != '' and bMashupInstaller:
        command = 'copy /Y ' + icoFile + '.bk ' + icoFile
        os.system(command)
        command = 'del /Q /S ' + icoFile + '.bk'
        os.system(command)
        

#始终拿到所有项目名称-和buildswitch中的文件名匹配
def getSlns(product):
    checklogFile = ''
    if product == 'bdm':
        checklogFile = conf.checklog_file
    elif product == 'bdkv':
        checklogFile = conf.kvchecklog_file
    
    slns = []
    fileObj = open(checklogFile, 'r')
    try:
        try:
            for line in fileObj.readlines():
                slns.append(line[0:line.find(' ')])
        finally:
            fileObj.close()
    except Exception, e:
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
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    #noaction then return
    if not actValue:
        return []
    #gen lock/unlock actions for all compiled module and basic/stable
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/' + item + '.xml'
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
        except Exception, e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    commands.append(conf.sln_root + 'basic')
    commands.append(conf.sln_root + 'stable_proj')
    #commands.append(conf.sln_root + 'common_stage_proj')
    commands = list(set(commands))
    #already get all folders, now lock/unlock these folder
    cmd_details = []
    ecode = sys.getfilesystemencoding()
    for item in commands:
        infoFile = '..\\output\\svn\\' + item[item.rfind('\\') + 1:] + '.info'
        command = 'svn list --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk -R ' + item + ' > ' + infoFile
        os.system(command.encode(sys.getfilesystemencoding()))
        fh = open(infoFile)
        files = fh.readlines()
        fh.close()
        for f in files:
            f = f.strip(' \r\n')
            if f[-1] == '/' or f[-1] == '\\':
                continue
            if action == 'lock':
                cmd_details.append('svn lock --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --force ' + item + '/' + f.decode(ecode).encode('utf-8'))
            elif action == 'unlock':
                cmd_details.append('svn unlock --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --force ' + item + '/' + f.decode(ecode).encode('utf-8'))
    return cmd_details

    
#得到svn操作
def getSvnCommands(product, value):
    svnAction = 'update'
    if value == 2 or value == 4 or value == 5:
        svnAction = 'checkout'
    elif value == 1 or value == 3:
        svnAction = 'update'
    
    bForce = False
    if value == 1 or value == 2:
        bForce = True
    elif value == 3 or value == 4 or value == 5:
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
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    
    if revision == 'HEAD':
        revision = GetRemoteRevision()
    
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/' + item + '.xml'
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
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + svnDir + " " + conf.sln_root + dir
                elif svnAction == 'update':
                    commands.append("svn cleanup --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk " + conf.sln_root + dir)
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.sln_root + dir
                commands.append(command)
                break
        except Exception, e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    if svnAction == 'update':
        commands.append("svn cleanup --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk " + conf.sln_root + "basic")
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.sln_root + "basic")
        commands.append("svn cleanup --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk " + conf.sln_root + "stable_proj")
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.sln_root + "stable_proj")
    elif svnAction == 'checkout' and value != 5:
        if product == 'bdm':
            commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "basic_proj" + codeDir + " " + conf.sln_root + "basic")
        elif product == 'bdkv':
            commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "avbasic_proj" + codeDir + " " + conf.sln_root + "basic")
        commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "stable_proj" + codeDir + " " + conf.sln_root + "stable_proj")
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
            secondPart = line[index + 2:]
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
                secondPart = line[index + 2:]
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
    
    if str.find('$revision') == -1 and str.find('$version') == -1 and str.find('$timestamp') == -1:
        return (str,revision)

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
            remote_version_folder = conf.svn_url + 'avbasic_proj' + codeDir + '/Tools/KVSetupScript'
            local_version_folder = '..\\output\\svn\\KVSetupScript'
            local_version_file = '../output/svn/KVSetupScript/BDKV_setup.nsi'
        command = 'rd /Q /S ' + local_version_folder
        os.system(command)
        command = 'svn checkout --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision ' + revision + ' ' + remote_version_folder + ' ' + local_version_folder
        os.system(command)
    f = open(local_version_file)
    version_lines = f.readlines()
    f.close()
    for line in version_lines:
        index = line.find('!define RELEASE_VERSION  ')
        if index != -1:
            secondPart = line[index + 25:]
            version = secondPart.strip('" \r\n')
            if code_revision != '':
                try:
                    version = '%d' % (int(version) + 1)
                except Exception, e:
                    print e
            break
    if revision == '' or version == '':
        return (str, revision)
    else:
        str = str.replace('$revision', 'r' + revision)
        str = str.replace('$version', 'v' + version)
        tst = '%f' % time.time()
        str = str.replace('$timestamp', 't' + tst)
        return (str, revision)

def getMarkupCodeCommands(product, value):
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
                    tokens = node.getAttribute('value').split(';')
                    if len(tokens) != 2:
                        codeDir = '/trunk'
                        code_revision = ''
                    else:
                        codeDir = '/' + tokens[0].strip('/ ')
                        code_revision = tokens[1].strip(' ')
                break
    except Exception, e:
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
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    
    #whether to xmarkup
    xmarkup = False
    try:
        dom = xml.dom.minidom.parse('./BuildSwitch/Misc.xml')
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'xmarkup':
                val = node.getAttribute('value')
                if val == '1':
                    xmarkup = True
                    break
    except Exception, e:
        logging.error("error occers when parsing xml : misc.xml")
        logging.error(e)
        
    #svn commands
    if markupType == '' or markupValue == '' or markupType == 'none':
        return []
    else:
        actType = markupType
        (markupValue, revision) = ExpendMarkupValue(product, markupValue, code_revision, codeDir)
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
            confFile = './BuildSwitch/' + item + '.xml'
            try:
                dom = xml.dom.minidom.parse(confFile)
                root = dom.documentElement
                dir = root.getAttribute('dir')
                svnDir = root.getAttribute('svnDir')
                #xmarkup & all build == '0' --> continue
                bSel = False
                for node in root.childNodes:
                    if node.nodeType != node.ELEMENT_NODE:
                        continue
                    if '1' == node.getAttribute('build'):
                        bSel = True
                        break
                if (not bSel) and xmarkup:
                    continue
                
                if not svnDir:
                    svnDir = dir + codeDir
                if actType[0] == '+':
                    command = "svn copy --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + svnDir + " " + conf.svn_url + dir + markupType + markupValue + ' -m "' + msg + '"'
                elif actType[0] == '-':
                    command = "svn delete " + conf.svn_url + dir + markupType + markupValue + ' -m "' + msg + '"'
                commands.append(command)
            except Exception, e:
                logging.error("error occers when parsing xml or run command:")
                logging.error(e)
        #add basic and stable
        if actType[0] == '+' and (not xmarkup):
            if product == 'bdm':
                commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "basic_proj" + codeDir + " " + conf.svn_url + "basic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            elif product == 'bdkv':
                commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "avbasic_proj" + codeDir + " " + conf.svn_url + "avbasic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "stable_proj" + codeDir + " " + conf.svn_url + "stable_proj" + markupType + markupValue + ' -m "' + msg + '"')
            #commands.append("svn copy --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision " + revision + " " + conf.svn_url + "common_stage_proj" + codeDir + " " + conf.svn_url + "common_stage_proj" + markupType + markupValue + ' -m "' + msg + '"')
        elif actType[0] == '-' and (not xmarkup):
            if product == 'bdm':
                commands.append("svn delete " + conf.svn_url + "basic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            elif product == 'bdkv':
                commands.append("svn delete " + conf.svn_url + "avbasic_proj" + markupType + markupValue + ' -m "' + msg + '"')
            commands.append("svn delete " + conf.svn_url + "stable_proj" + markupType + markupValue + ' -m "' + msg + '"')
            #commands.append("svn delete " + conf.svn_url + "common_stage_proj" + markupType + markupValue + ' -m "' + msg + '"')
        commands = list(set(commands))
        return commands
    
def getBuildCommands(product, value):
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
    if value == 1 or value == 2:
        bForce = False
    elif value == 3 or value == 4:
        bForce = True
    
    commands = []
    slns = getSlns(product)
    for item in slns:
        confFile = './BuildSwitch/' + item + '.xml'
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
            writer = open(confFile, 'w')
            dom.writexml(writer)
            writer.close()
        except Exception, e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    return commands
    
    
def getInstallOptions():
    pkgFile = './BuildSwitch/Package.xml'
    try:
        dom = xml.dom.minidom.parse(pkgFile)
        root = dom.documentElement
        bInstall = False if root.getAttribute('install') == '0' else True
        bInstallMini = False if root.getAttribute('install_mini') == '0' else True
        bInstallFull = False if root.getAttribute('install_full') == '0' else True
        bInstallUpdate = False if root.getAttribute('install_update') == '0' else True
        bInstallSilence = False if root.getAttribute('install_silence') == '0' else True
        bInstallDefense = False if root.getAttribute('install_defense') == '0' else True
        return (bInstall, bInstallMini, bInstallFull, bInstallUpdate, bInstallSilence, bInstallDefense)
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
        
def getViruslibVersion():
    vlibVersionFile = conf.sln_root + 'basic\\KVOutput\\virusdb\\version'
    try:
        ctx = comm.getMsg(vlibVersionFile)
        return ctx
    except Exception, e:
        logging.error("error occers when getting vlib version")
        logging.error(e)

def buildSilentPackage(obj, product, type, file_i=''):
    silentNsiFile = ''
    nsiFile = ''
    if product == 'bdm':
        if type == 'mini':
            silentNsiFile = conf.bdm_netinstall_silent_file
            nsiFile = conf.bdm_netinstall_silent_file
        elif type == 'normal' or type == 'full':
            silentNsiFile = conf.bdm_install_silent_file
            nsiFile = conf.bdm_nsifile_daily
    elif product == 'bdkv':
        if type == 'mini':
            silentNsiFile = conf.bdkv_netinstall_silent_file
            nsiFile = conf.bdkv_netinstall_file
        elif type == 'normal' or type == 'full':
            silentNsiFile = conf.bdkv_install_silent_file
            nsiFile = conf.bdkv_nsifile_daily
    if len(file_i) > 0:
        nsiFile = file_i
        if type == 'mini':
            silentNsiFile = file_i
    if not os.path.exists(nsiFile):
        return
    file_r = open(silentNsiFile)
    lines = file_r.readlines()
    file_r.close()
    for index in range(len(lines)):
        if lines[index].find('#silent#') != -1:
            lines[index] = 'Strcpy $varIsSilence "1"    #silent#\r\n'
        if lines[index].find("#StartMain#") != -1:
            lines[index] = 'Strcpy $StartMain "1"    #StartMain#\r\n'
    file_w = open(silentNsiFile, "w")
    file_w .writelines(lines)
    file_w .close()
    #do install
    command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + nsiFile
    #os.system(command.encode(sys.getfilesystemencoding()))
    finalBuildpackage(product, type, command, nsiFile)
    #clean
    file_r = open(silentNsiFile)
    lines = file_r.readlines()
    file_r.close()
    for index in range(len(lines)):
        if lines[index].find('#silent#') != -1:
            lines[index] = '#Strcpy $varIsSilence "1"    #silent#\r\n'
        if lines[index].find("#StartMain#") != -1:
            lines[index] = '#Strcpy $StartMain "1"    #StartMain#\r\n'
    file_w = open(silentNsiFile, "w")
    file_w .writelines(lines)
    file_w .close()

def buildDefensePackage(obj, product, type, file_i='', bSilent=False):
    #(bInstall, bInstallMini, bInstallFull, bInstallUpdate, bInstallSilence, bInstallDefense) = getInstallOptions()
    #if not bInstallDefense:
    #    return
    silentNsiFile = ''
    nsiFile = ''
    defenseNsiFile = ''
    if product == 'bdm':
        if type == 'mini':
            silentNsiFile = conf.bdm_netinstall_silent_file
            nsiFile = conf.bdm_netinstall_silent_file
        elif type == 'normal' or type == 'full':
            silentNsiFile = conf.bdm_install_silent_file
            nsiFile = conf.bdm_nsifile_daily
    elif product == 'bdkv':
        if type == 'mini':
            silentNsiFile = conf.bdkv_netinstall_silent_file
            nsiFile = conf.bdkv_netinstall_file
        elif type == 'normal' or type == 'full':
            silentNsiFile = conf.bdkv_install_silent_file
            nsiFile = conf.bdkv_nsifile_daily
    if len(file_i) > 0:
        nsiFile = file_i
        if type == 'mini':
            silentNsiFile = file_i
    if not os.path.exists(nsiFile):
        return
    defenseNsiFile = nsiFile + '.defense.nsi'
    #silent modify
    if bSilent:
        file_r = open(silentNsiFile)
        lines = file_r.readlines()
        file_r.close()
        for index in range(len(lines)):
            if lines[index].find('#silent#') != -1:
                lines[index] = 'Strcpy $varIsSilence "1"    #silent#\r\n'
            if lines[index].find("#StartMain#") != -1:
                lines[index] = 'Strcpy $StartMain "1"    #StartMain#\r\n'
        file_w = open(silentNsiFile, "w")
        file_w .writelines(lines)
        file_w .close()
    #productinfo modify
    file_r = open(nsiFile)
    lines = file_r.readlines()
    file_r.close()
    for index in range(len(lines)):
        if lines[index].find('VIAddVersionKey /LANG=2052 "ProductName"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "ProductName" ""\r\n'
        if lines[index].find('VIAddVersionKey /LANG=2052 "CompanyName"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "CompanyName" ""\r\n'
        if lines[index].find('VIAddVersionKey /LANG=2052 "LegalTrademarks"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "LegalTrademarks" ""\r\n'
        if lines[index].find('VIAddVersionKey /LANG=2052 "LegalCopyright"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "LegalCopyright" ""\r\n'
        if lines[index].find('VIAddVersionKey /LANG=2052 "FileDescription"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "FileDescription" ""\r\n'
        if lines[index].find('OutFile') != -1:
            index_p = lines[index].find('.exe')
            newOutput = lines[index][0:index_p] + '_Defense' + lines[index][index_p:]
            lines[index] = newOutput
    file_w = open(defenseNsiFile, "w")
    file_w .writelines(lines)
    file_w .close()
    #do install
    command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + defenseNsiFile
    #os.system(command.encode(sys.getfilesystemencoding()))
    finalBuildPackage(product,type,command, defenseNsiFile)
    #clean
    #silent
    if bSilent:
        file_r = open(silentNsiFile)
        lines = file_r.readlines()
        file_r.close()
        for index in range(len(lines)):
            if lines[index].find('#silent#') != -1:
                lines[index] = '#Strcpy $varIsSilence "1"    #silent#\r\n'
            if lines[index].find("#StartMain#") != -1:
                lines[index] = '#Strcpy $StartMain "1"    #StartMain#\r\n'
        file_w = open(silentNsiFile, "w")
        file_w .writelines(lines)
        file_w .close()
    #productinfo
    command = 'del /Q /S ' + defenseNsiFile
    os.system(command)


def buildSupplyidPackage(obj, product, type, bSilent, bDefense):#type: mini, normal, full
    insFile = ''
    vInstallFile = ''
    miniSilentFile = ''
    key = ''
    installerPath = ''
    default_normal_supplyid = ''
    default_mini_supplyid = ''
    configIniFile = ''
    default_installer_supplyid = []
    if len(type) > 0:
        key = type[0]

    if product == 'bdm':
        default_normal_supplyid = '50000'
        default_mini_supplyid = '50001'
        configIniFile = conf.sln_root + 'basic\\tools\\BDMNetInstall\\res\\config.ini'
        if key == 'm':
            insFile = conf.sln_root + 'basic\\tools\\BDMNetInstall\\BDMNetInstall.nsi'
            miniSilentFile = conf.sln_root + 'basic\\tools\\BDMNetInstall\\include\\buildline.nsi'
        else:
            insFile = conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
            vInstallFile = conf.sln_root + 'basic\\tools\\SetupScript\\include\\BDM_install.nsi'
        installerPath = '..\\setup\\'
        default_installer_supplyid = conf.bdm_default_installer_supplyid
    elif product == 'bdkv':
        default_normal_supplyid = '10000'
        default_mini_supplyid = '10001'
        configIniFile = conf.sln_root + 'basic\\tools\\KVNetInstall\\res\\config.ini'
        if key == 'm':
            insFile = conf.sln_root + 'basic\\tools\\KVNetInstall\\KVNetInstall.nsi'
            miniSilentFile = conf.sln_root + 'basic\\tools\\KVNetInstall\\include\\buildline.nsi'
        else:
            insFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
            vInstallFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_install.nsi'
        installerPath = '..\\kvsetup\\'
        default_installer_supplyid = conf.bdkv_default_installer_supplyid
    confFile = './BuildSwitch/Misc.xml'
    slist = []
    #read supplyid list
    try:
        dom = xml.dom.minidom.parse(confFile)
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'supplyid':
                value = node.getAttribute('value')
                slist = value.split(',')
                break
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    #do it
    for item in slist:
        if len(item) < 2:
            continue
        if item[0] != key:
            continue
        if item in default_installer_supplyid:
            continue
        token = '_Sid_' + item[1:]
        if bSilent:
            token += '_Silent'
        supplyid = item[1:]
        newInsFile = insFile[:-4] + '_Sid_' + item[1:] + '.nsi'
        #nsis backup
        command = 'copy /Y ' + insFile + ' ' + newInsFile
        os.system(command.encode(sys.getfilesystemencoding()))
        file_r = open(newInsFile)
        lines = file_r.readlines()
        file_r.close()
        installerFullName = comm.getInstallerFullName(product)
        installerVersion = comm.getInstallerVersion(product)
        for index in range(len(lines)):
            if lines[index].find('OutFile') != -1:
                if key == 'm':
                    lines[index] = 'OutFile "' + installerPath + installerFullName + '_Online%s.exe"\r\n' % token
                elif key == 'n':
                    lines[index] = 'OutFile "' + installerPath + installerFullName + '%s.exe"\r\n' % token
                elif key == 'f':
                    lines[index] = 'OutFile "' + installerPath + installerFullName + '_Full%s.exe"\r\n' % token
            if lines[index].find('VIProductVersion') != -1:
                lines[index] = 'VIProductVersion "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "FileVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "ProductVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"\r\n' % installerVersion
        file_w = open(newInsFile, "w")
        file_w .writelines(lines)
        file_w .close()
        #nsis backup again
        ctx = ''
        if key != 'm':
            file_r = open(vInstallFile)
            lines = file_r.readlines()
            file_r.close()
            for index in range(len(lines)):
                if lines[index].find('StrCpy $SupplyID') != -1:
                    lines[index] = 'StrCpy $SupplyID "%s"\r\n' % supplyid
            file_w = open(vInstallFile, "w")
            file_w .writelines(lines)
            file_w .close()
        else:
            file_r = open(miniSilentFile)
            lines = file_r.readlines()
            file_r.close()
            token = '!define SUPPLYID "%s"' % default_mini_supplyid
            for index in range(len(lines)):
                if lines[index].find(token) != -1:
                    lines[index] = '!define SUPPLYID "%s"\r\n' % supplyid
            file_w = open(miniSilentFile, "w")
            file_w .writelines(lines)
            file_w .close()

            ctx = comm.getMsg(configIniFile)
            ctx_new = ctx.replace(default_mini_supplyid, item[1:])
            comm.saveFile(configIniFile, ctx_new)
        #do install
        if not bDefense:
            if not bSilent:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + newInsFile
                #os.system(command.encode(sys.getfilesystemencoding()))
                finalBuildPackage(product,type,command, newInsFile)
            else:
                buildSilentPackage(obj, product, type, newInsFile)
        else:
            buildDefensePackage(obj, product, type, newInsFile, bSilent)
        #clean
        command = 'del /Q /S ' + newInsFile
        os.system(command)
        if key != 'm':
            file_r = open(vInstallFile)
            lines = file_r.readlines()
            file_r.close()
            for index in range(len(lines)):
                if lines[index].find('StrCpy $SupplyID') != -1:
                    lines[index] = 'StrCpy $SupplyID "%s"\r\n' % default_normal_supplyid
            file_w = open(vInstallFile, "w")
            file_w .writelines(lines)
            file_w .close()
        else:
            file_r = open(miniSilentFile)
            lines = file_r.readlines()
            file_r.close()
            for index in range(len(lines)):
                if lines[index].find('!define SUPPLYID') != -1:
                    lines[index] = '!define SUPPLYID "%s"\r\n' % default_mini_supplyid
            file_w = open(miniSilentFile, "w")
            file_w .writelines(lines)
            file_w .close()
            comm.saveFile(configIniFile, ctx)

def installMiniPackage(obj, product, bSupplyid=False, bSilent=False, bDefense=False):
    installerPath = ''
    defaultSupplyid = ''
    if product == 'bdm':
        defaultSupplyid = 'm50001'
        installerPath = '..\\setup\\'
    elif product == 'bdkv':
        defaultSupplyid = 'm10001'
        installerPath = '..\\kvsetup\\'
    #nsis backup
    newNetInstallFile = conf.sln_root + 'basic\\tools\\KVNetInstall\\KVNetInstall_Dummy.nsi'
    command = 'copy /Y ' + conf.sln_root + 'basic\\tools\\KVNetInstall\\KVNetInstall.nsi' + ' ' + newNetInstallFile
    os.system(command.encode(sys.getfilesystemencoding()))
    file_r = open(newNetInstallFile)
    lines = file_r.readlines()
    file_r.close()
    installerFullName = comm.getInstallerFullName(product)
    installerVersion = comm.getInstallerVersion(product)
    for index in range(len(lines)):
        if lines[index].find('OutFile') != -1:
            if bSilent:
                lines[index] = 'OutFile "' + installerPath + installerFullName + '_Online_Silent.exe"\r\n'
            else:
                lines[index] = 'OutFile "' + installerPath + installerFullName + '_Online.exe"\r\n'
        if lines[index].find('VIProductVersion') != -1:
            lines[index] = 'VIProductVersion "%s"\r\n' % installerVersion
        if lines[index].find('VIAddVersionKey /LANG=2052 "FileVersion"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"\r\n' % installerVersion
        if lines[index].find('VIAddVersionKey /LANG=2052 "ProductVersion"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"\r\n' % installerVersion
    file_w = open(newNetInstallFile, "w")
    file_w .writelines(lines)
    file_w .close()
    #do it
    #read supplyid list
    confFile = './BuildSwitch/Misc.xml'
    slist = []
    try:
        dom = xml.dom.minidom.parse(confFile)
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'supplyid':
                value = node.getAttribute('value')
                slist = value.split(',')
                break
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    if defaultSupplyid in slist:
        if not bDefense:
            if not bSilent:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + newNetInstallFile
                obj.report('wk-build-log', command)
                #os.system(command.encode(sys.getfilesystemencoding()))
                finalBuildPackage(product,'mini',command, newNetInstallFile)
            else:
                buildSilentPackage(obj, product, 'mini', newNetInstallFile)
        else:
            buildDefensePackage(obj, product, 'mini', newNetInstallFile, bSilent)
    #clean
    command = 'del /Q /S ' + newNetInstallFile
    os.system(command.encode(sys.getfilesystemencoding()))
    #supplyid
    if bSupplyid:
        buildSupplyidPackage(obj, product, 'mini', bSilent, bDefense)

def installNormalPackage(obj, product, bSupplyid=False, bSilent=False, bDefense=False):
    nsiFile = ''
    bkOutput = ''
    installerPath = ''
    #read supplyid list
    confFile = './BuildSwitch/Misc.xml'
    slist = []
    defaultSupplyid = ''
    try:
        dom = xml.dom.minidom.parse(confFile)
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'supplyid':
                value = node.getAttribute('value')
                slist = value.split(',')
                break
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
    if product == 'bdm':
        defaultSupplyid = 'n50000'
        nsiFile = conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
        bkOutput = 'OutFile "..\setup\BaiduAn_Setup_${BUILD_BASELINE}.exe"\r\n'
        installerPath = '..\\setup\\'
    elif product == 'bdkv':
        defaultSupplyid = 'n10000'
        nsiFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
        bkOutput = 'OutFile "..\kvsetup\Baidusd_Setup_${BUILD_BASELINE}.exe"\r\n'
        installerPath = '..\\kvsetup\\'
    if defaultSupplyid in slist:
        file_r = open(nsiFile)
        lines = file_r.readlines()
        file_r.close()
        installerFullName = comm.getInstallerFullName(product)
        installerVersion = comm.getInstallerVersion(product)
        for index in range(len(lines)):
            if lines[index].find('OutFile') != -1:
                if bSilent:
                    lines[index] = 'OutFile "' + installerPath + installerFullName + '_Silent.exe"\r\n'
                else:
                    lines[index] = 'OutFile "' + installerPath + installerFullName + '.exe"\r\n'
            if lines[index].find('VIProductVersion') != -1:
                lines[index] = 'VIProductVersion "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "FileVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"\r\n' % installerVersion
            if lines[index].find('VIAddVersionKey /LANG=2052 "ProductVersion"') != -1:
                lines[index] = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"\r\n' % installerVersion
        file_w = open(nsiFile, "w")
        file_w .writelines(lines)
        file_w .close()
        
        if not bDefense:
            if not bSilent:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + nsiFile
                #os.system(command.encode(sys.getfilesystemencoding()))
                finalBuildPackage(product,'normal',command, nsiFile)
            else:
                buildSilentPackage(obj, product, 'normal', nsiFile)
        else:
            buildDefensePackage(obj, product, 'normal', nsiFile, bSilent)
        
        file_r = open(nsiFile)
        lines = file_r.readlines()
        file_r.close()
        for index in range(len(lines)):
            if lines[index].find('OutFile') != -1:
                lines[index] = bkOutput
        file_w = open(nsiFile, "w")
        file_w .writelines(lines)
        file_w .close()
    #supplyid
    if bSupplyid:
        buildSupplyidPackage(obj, product, 'normal', bSilent, bDefense)

def installKvFullPackage(obj, product, bSupplyid=False, bSilent=False, bDefense=False):
    #prepare
    confFile = './BuildSwitch/Misc.xml'
    slist = []
    try:
        dom = xml.dom.minidom.parse(confFile)
        root = dom.documentElement
        for node in root.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            name = node.getAttribute('name')
            if name == 'supplyid':
                value = node.getAttribute('value')
                slist = value.split(',')
                break
    except Exception, e:
        logging.error("error occers when parsing xml or run command:")
        logging.error(e)
        
    #only bdkv now
    command = 'copy /Y ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    os.system(command.encode(sys.getfilesystemencoding()))
    setupFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    file_r = open(setupFile)
    lines = file_r.readlines()
    file_r.close()
    installerFullName = comm.getInstallerFullName(product)
    installerVersion = comm.getInstallerVersion(product)
    for index in range(len(lines)):
        if lines[index].find('OutFile') != -1:
            if bSilent:
                lines[index] = 'OutFile "..\\kvsetup\\' + installerFullName + '_Full_Silent.exe"\r\n'
            else:
                lines[index] = 'OutFile "..\\kvsetup\\' + installerFullName + '_Full.exe"\r\n'
        if lines[index].find('VIProductVersion') != -1:
            lines[index] = 'VIProductVersion "%s"\r\n' % installerVersion
        if lines[index].find('VIAddVersionKey /LANG=2052 "FileVersion"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "FileVersion" "%s"\r\n' % installerVersion
        if lines[index].find('VIAddVersionKey /LANG=2052 "ProductVersion"') != -1:
            lines[index] = 'VIAddVersionKey /LANG=2052 "ProductVersion" "%s"\r\n' % installerVersion
    file_w = open(setupFile, "w")
    file_w .writelines(lines)
    file_w .close()
    
    command = 'rd /Q /S ..\\output\\backup\\bases\\'
    os.system(command)
    command = 'xcopy /Y /E /S ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases ..\output\\backup\\bases\\'
    os.system(command)
    command = 'rd /Q /S ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases'
    os.system(command)
    command = 'xcopy /Y /E /S ' + conf.sln_root + 'basic\\kvoutput\\virusdb\\bases ' + conf.sln_root + 'basic\\kvoutput\\binrelease\\kav\\bases\\'
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
            if lines[index].find('MACRO_ANTIVIRUS_UPDATETIME') != -1:
                lines[index] = '!define MACRO_ANTIVIRUS_UPDATETIME      "%s"\r\n' % vlibVersion
        file_w = open(vInstallFile, "w")
        file_w .writelines(lines)
        file_w .close()
        
    command = 'copy /Y ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_install.nsi ..\\output\\backup\\KV_install.nsi'
    os.system(command.encode(sys.getfilesystemencoding()))
    vInstallFile = conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_install.nsi'
    file_r = open(vInstallFile)
    lines = file_r.readlines()
    file_r.close()
    for index in range(len(lines)):
        if lines[index].find('StrCpy $SupplyID') != -1:
            lines[index] = 'StrCpy $SupplyID "10015"\r\n'
    file_w = open(vInstallFile, "w")
    file_w .writelines(lines)
    file_w .close()
    
    #install
    if not bDefense:
        if 'f10015' in slist:
            if not bSilent:
                command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL /SOLID lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
                #os.system(command.encode(sys.getfilesystemencoding()))
                finalBuildPackage(product,'full',command, conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi')
            else:
                buildSilentPackage(obj, product, 'full', conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi')
    else:
        buildDefensePackage(obj, product, 'full', conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi', bSilent)
    
    #supplyid
    if bSupplyid:
        buildSupplyidPackage(obj, product, 'full', bSilent, bDefense)
        
    #clean
    command = 'del /Q /S ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup_full.nsi'
    os.system(command)
    command = 'copy /Y ..\\output\\backup\\KV_Language.nsh ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_Language.nsh'
    os.system(command)
    command = 'copy /Y ..\\output\\backup\\KV_install.nsi ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\KV_install.nsi'
    os.system(command)
    command = 'del /Q /S ..\\output\\backup\\KV_Language.nsh'
    os.system(command)
    command = 'del /Q /S ..\\output\\backup\\KV_install.nsi'
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
    rewrite_version.main(4, ['rewrite_version.py', product, buildType, 'update'])
    
def genMailMsg(product):
    mailFile = ''
    installerFolder = ''
    buildIdFile = ''
    verify_log_file = ''
    if product == 'bdm':
        mailFile = conf.bdm_mail_file
        installerFolder = conf.ftpPathNameR
        buildIdFile = conf.buildIdFile
        logDir = conf.log_path
        verify_log_file = conf.verify_log_file
    elif product == 'bdkv':
        mailFile = conf.bdkv_mail_file
        installerFolder = conf.ftpKVPathNameR
        buildIdFile = conf.kvBuildIdFile
        logDir = conf.kvlog_path
        verify_log_file = conf.kvverify_log_file
    fp = open(mailFile, 'w')
    #fp.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body>')
    fp.write('Dailybuild notification mail\r\n\r\n')
    fp.write('\r\nBuilding Log(s):\r\n----------------------------------------------------------------------------------------\r\n')
    for file in os.listdir(logDir):
        if file[-3:] == 'log':
            errLog = comm.getMsg(logDir + file)
            fp.write(file + '\r\n')
            if errLog != '':
                fp.write(errLog + '\r\n\r\n')
            else:
                fp.write('ok\r\n\r\n')
                
    if os.path.exists(verify_log_file):
        fp.write('\r\n\r\nFile Verify Log:\r\n----------------------------------------------------------------------------------------\r\n')
        ctx = comm.getMsg(verify_log_file)
        fp.write(ctx)
    
    fp.write('\r\n\r\nInstaller Folder:\r\n----------------------------------------------------------------------------------------\r\n')
    id = comm.getMsg(buildIdFile)
    installerDir = installerFolder + '1.0.0.%s\\' % id
    fp.write(installerDir)
    
    fp.write('\r\n\r\nYou will receive this email when daily/nighty build finishes.Do NOT want to be bothered? RTX liuheng.')
    #fp.write('</body></html>')
    fp.close()

def makeBinplace(product, files, buildtype):
    if product == 'bdm':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\Output\\Symbols\\' + buildtype + '\\Full -r ' + conf.sln_root + 'basic\\Output\\Symbols\\' + buildtype + '\\ -:DEST BDM ' + conf.sln_root + files
    elif product == 'bdkv':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\' + buildtype + '\\Full -r ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\' + buildtype + '\\ -:DEST BDKV ' + conf.sln_root + files

def genSymbols(product):
    commands = []
    if product == 'bdm':
        #release
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\*.exe', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\bdmantivirus\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\FTSOManager\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\FTSWManager\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmkvscanplugin\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmhomepageplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmmainframeplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmsomanagerplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmswmanagerplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmtrayplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\rtpplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmpatcherplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinRelease\\plugins\\bdmsafeplugins\\*.dll', 'Release'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Full\\BDM\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Stripped\\BDM\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Release /t "THIRD"')
        #debug
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\*.exe', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\bdmantivirus\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\FTSOManager\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\FTSWManager\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmkvscanplugin\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmhomepageplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmmainframeplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmsomanagerplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmswmanagerplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmtrayplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\rtpplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BibDebug\\plugins\\bdmpatcherplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdm', 'basic\\Output\\BinDebug\\plugins\\bdmsafeplugins\\*.dll', 'Debug'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Debug\\Full\\BDM\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Debug /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Debug\\Stripped\\BDM\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Debug /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Debug\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Debug /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Debug\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Debug /t "THIRD"')
    elif product == 'bdkv':
        #release
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\*.exe', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\bdmantivirus\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\bdmsysrepair\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\websafe\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\drivers\\*.sys', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\drivers\\x86\\*.sys', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\drivers\\x64\\*.sys', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\drivers\\x64\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\plugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\plugins\\bdkv\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll', 'Release'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll', 'Release'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Full\\BDKV\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Stripped\\BDKV\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Release /t "THIRD"')
        #debug
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\*.exe', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\bdmantivirus\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\bdmsysrepair\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\websafe\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\drivers\\*.sys', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\plugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\plugins\\bdkv\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\plugins\\bdkvtrayplugins\\*.dll', 'Debug'))
        commands.append(makeBinplace('bdkv', 'basic\\KVOutput\\BinDebug\\plugins\\bdkvrtpplugins\\*.dll', 'Debug'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Debug\\Full\\BDKV\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Debug /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Debug\\Stripped\\BDKV\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Debug /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Debug\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Full\\Debug /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Debug\\*.pdb /s \\\\10.52.174.35\\public\\Symbols\\Stripped\\Debug /t "THIRD"')
    return commands

def genPrebuildActions(product, value):
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
            commands.append('del /Q ' + conf.bdm_mail_file)
            commands.append('del /Q ' + conf.verify_log_file)
        elif product == 'bdkv':
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvversionbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\include\\buildline.nsi')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\kvsetup\\*.exe')
            commands.append('del /Q ..\\output\\kvsetup\\*.exe')
            commands.append('del /Q ..\\output\\kverr\\*.log')
            commands.append('del /Q ' + conf.bdkv_mail_file)
            commands.append('del /Q ' + conf.kvverify_log_file)
    if value == 2:
        commands.append('del /Q /S ' + conf.sln_root + 'basic\\lib')
        if product == 'bdm':
            commands.append('del /Q /S ' + conf.sln_root + 'basic\\Output')
        elif product == 'bdkv':
            commands.append('del /Q /S ' + conf.sln_root + 'basic\\KVOutput')
    commands.append('svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk --revision HEAD ' + conf.sln_root + 'basic')
    return commands

##############################################

class BuildStep:
    g_t_weight = 0
    g_c_weight = 0
    def __init__(self, n, v, o, w, p):
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
        self.update_step(0, bFinish=True)
    
    def report(self, msrc, msg):
        if len(self.para) == 0:
            logging.info(msg)
        elif self.para[0] == 'wk-build-log':
            sid = self.para[1]
            ws = self.para[2]
            #整饰特殊字符
            msg = msg.replace('\\', '/')
            msg = msg.replace('"', ' ')
            msg = msg.replace('\'', ' ')
            msg = msg.replace('\r', ' ')
            msg = msg.replace('\n', ' ')
            content = '{"msrc":"%s","content":"%s"}' % (msrc, msg)
            logging.info('send message from worker, sid:%s, message:%s' % (sid, content))
            ws.send(content)
    
    def update_step(self, w, bFinish=False):
        if self.cweight == self.weight:
            pass
        elif self.cweight + w >= self.weight or bFinish:
            BuildStep.g_c_weight += self.weight - self.cweight
            self.cweight = self.weight
            percentage = float(BuildStep.g_c_weight) / float(BuildStep.g_t_weight) * 100
            msg = '%d' % percentage
            logging.info('cweight : %d, weight : %d, g_c_weight : %d, g_t_weight : %d, w : %d', self.cweight, self.weight, BuildStep.g_c_weight, BuildStep.g_t_weight, w)
            self.report('wk-build-progress', msg)
        else:
            BuildStep.g_c_weight += w
            self.cweight += w
            percentage = float(BuildStep.g_c_weight) / float(BuildStep.g_t_weight) * 100
            msg = '%d' % percentage
            logging.info('cweight : %d, weight : %d, g_c_weight : %d, g_t_weight : %d, w : %d', self.cweight, self.weight, BuildStep.g_c_weight, BuildStep.g_t_weight, w)
            self.report('wk-build-progress', msg)

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
            commands = genPrebuildActions('bdm', self.value)
            for item in commands:
                self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            commands = genPrebuildActions('bdkv', self.value)
            for item in commands:
                self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            command = 'svn info --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.svn_url + ' > ' + conf.svn_remote_info_file
            os.system(command)
            commands = getSvnCommands('bdm', self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No svn commands')
            else:
                for item in commands:
                    if item.find('checkout') != -1:
                        subdir = item[item.find(conf.svn_url) + len(conf.svn_url):]
                        subdir = subdir[0:subdir.find('/')]
                        if subdir.lower() == 'basic_proj' or subdir.lower() == 'avbasic_proj':
                            subdir = 'basic'
                        command = 'rd /Q /S ..\\..\\' + subdir
                        self.report('wk-build-log', command)
                        os.system(command.encode(sys.getfilesystemencoding()))
                        self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    else:
                        self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            command = 'svn info --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.svn_url + ' > ' + conf.svn_remote_info_file
            os.system(command)
            commands = getSvnCommands('bdkv', self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No svn commands')
            else:
                for item in commands:
                    if item.find('checkout') != -1:
                        subdir = item[item.find(conf.svn_url) + len(conf.svn_url):]
                        subdir = subdir[0:subdir.find('/')]
                        if subdir.lower() == 'basic_proj' or subdir.lower() == 'avbasic_proj':
                            subdir = 'basic'
                        command = 'rd /Q /S ..\\..\\' + subdir
                        self.report('wk-build-log', command)
                        os.system(command.encode(sys.getfilesystemencoding()))
                        self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
                        os.system(item.encode(sys.getfilesystemencoding()))
                    else:
                        self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            commands = genSvnLockActions('bdm', 'lock', self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('bCRjzYKzk','XXXXXX'))
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
            commands = genSvnLockActions('bdkv', 'lock', self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('bCRjzYKzk','XXXXXX'))
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
            self.report('wk-build-log', 'Adjusting buildversion')
            comm.setBuildNumber('bdm', '0', False)
            command = 'python rewrite_version.py bdm daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdm', 'daily'])
        elif self.value == 1:
            command = 'python rewrite_version.py bdm daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdm', 'daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdm version'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdm', 'version'])
        BuildStep.act(self)

    
class KVRewriteVersion(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV update build version and resource definition"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Adjusting buildversion')
            comm.setBuildNumber('bdkv', '0', False)
            command = 'python rewrite_version.py bdkv daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdkv', 'daily'])
        elif self.value == 1:
            command = 'python rewrite_version.py bdkv daily'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdkv', 'daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdkv version'
            self.report('wk-build-log', command)
            rewrite_version.main(3, ['rewrite_version.py', 'bdkv', 'version'])
        BuildStep.act(self)
    
##############################################
# 0,1

class Rcgen(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM rcgen operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            command = 'python rcgen.py bdm'
            self.report('wk-build-log', command)
            rcgen.main(2, ['rcgen.py', 'bdm'])
        BuildStep.act(self)
    
class KVRcgen(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV rcgen operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            command = 'python rcgen.py bdkv'
            self.report('wk-build-log', command)
            rcgen.main(2, ['rcgen.py', 'bdkv'])
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
            commands = getBuildCommands('bdm', self.value)
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
                        self.report('wk-build-log', '<h5>PRJ0002 error found, try rebuilding specific solution<h5>')
                        self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
                        bReCompiler = False
                        for item in commands:
                            if item.find(conf.log_path + file) != -1:
                                bReCompiler = True
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
                except Exception, e:
                    logging.error("error occers when parsing xml or run command:")
                    logging.error(e)
                if bIgnoreFault:
                    msg = '<h5>Build error(s) found, xbuild continues, please handle these error(s) below later : </h5>'
                    self.report('wk-build-log', msg)
                else:
                    msg = '<h5>Build error(s) found, xbuild quit, please handle these error(s) below : </h5>'
                    self.report('wk-status-change', 'error')
                    self.report('wk-build-log', msg)
                for file in os.listdir(conf.log_path):
                    if file[-3:] == 'log':
                        errLog = comm.getMsg(conf.log_path + file)
                        if errLog != '':
                            self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
                            self.report('wk-build-log', '<h5>' + file + '</h5>')
                            fp = open(conf.log_path + file)
                            lines = fp.readlines()
                            fp.close()
                            for line in lines:
                                self.report('wk-build-log', line)
                self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
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
            commands = getBuildCommands('bdkv', self.value)
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
                        self.report('wk-build-log', '<h5>PRJ0002 error found, try rebuilding specific solution<h5>')
                        self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
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
                except Exception, e:
                    logging.error("error occers when parsing xml or run command:")
                    logging.error(e)
                if bIgnoreFault:
                    msg = '<h5>Build error(s) found, xbuild continues, please handle these error(s) below later : </h5>'
                    self.report('wk-build-log', msg)
                else:
                    msg = '<h5>Build error(s) found, xbuild quit, please handle these error(s) below : </h5>'
                    self.report('wk-status-change', 'error')
                    self.report('wk-build-log', msg)
                for file in os.listdir(conf.kvlog_path):
                    if file[-3:] == 'log':
                        errLog = comm.getMsg(conf.kvlog_path + file)
                        if errLog != '':
                            self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
                            self.report('wk-build-log', '<h5>' + file + '</h5>')
                            fp = open(conf.kvlog_path + file)
                            lines = fp.readlines()
                            fp.close()
                            for line in lines:
                                self.report('wk-build-log', line)
                self.report('wk-build-log', '<h5>------------------------------------------------------------------------------------------------------------</h5>')
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
            command = 'python fileop.py mzip_res ' + conf.sln_root + 'basic\\Output\\SkinResources'
            self.report('wk-build-log', command)
            fileop.main(3,['fileop.py','mzip_res',conf.sln_root + 'basic\\Output\\SkinResources'])
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
            command = 'python fileop.py kv_mzip_res ' + conf.sln_root + 'basic\\KVOutput\\SkinResources'
            self.report('wk-build-log', command)
            fileop.main(3,['fileop.py','kv_mzip_res',conf.sln_root + 'basic\\KVOutput\\SkinResources'])
        BuildStep.act(self)
    
##############################################
# 0,1

class Rebase(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM rebase operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            command = conf.byp_bin_path + 'rebase.exe -d -b 0x60000000 ..\\..\\basic\\output\\binrelease\\*.dll ..\\..\\basic\\output\\binrelease\\bdmantivirus\\*.dll ..\\..\\basic\\output\\binrelease\\ftsomanager\\*.dll ..\\..\\basic\\output\\binrelease\\FTSWManager\\sw_si_assistor\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmkvscanplugin\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmmainframeplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\BDMSOManagerPlugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmswmanagerplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmtrayplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\RTPPlugins\\*.dll'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            command = conf.byp_bin_path + 'bind.exe -u ..\\..\\basic\\output\\binrelease\\*.dll ..\\..\\basic\\output\\binrelease\\bdmantivirus\\*.dll ..\\..\\basic\\output\\binrelease\\ftsomanager\\*.dll ..\\..\\basic\\output\\binrelease\\FTSWManager\\sw_si_assistor\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmkvscanplugin\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmmainframeplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\BDMSOManagerPlugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmswmanagerplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\bdmtrayplugins\\*.dll ..\\..\\basic\\output\\binrelease\\plugins\\RTPPlugins\\*.dll'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
        BuildStep.act(self)
    
class KVRebase(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV rebase operations"
    
    def act(self):
        if self.value == 0:
             self.report('wk-build-log', 'Passed')
        else:
            command = conf.byp_bin_path + 'rebase.exe -d -b 0x60000000 ..\\..\\basic\\kvoutput\\binrelease\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\bdmantivirus\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\bdmsysrepair\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkv\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkvrtpplugins\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkvtrayplugins\\*.dll'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            command = conf.byp_bin_path + 'bind.exe -u ..\\..\\basic\\kvoutput\\binrelease\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\bdmantivirus\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\bdmsysrepair\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkv\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkvrtpplugins\\*.dll ..\\..\\basic\\kvoutput\\binrelease\\plugins\\bdkvtrayplugins\\*.dll'
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
            fileop.main(4, ['fileop.py', 'kvsign', conf.sln_root + 'basic\\Output\\BinDebug\\', '*.exe'])
            command = 'python fileop.py kvsign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe'])

            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\Output\\BinDebug\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign_kav', conf.sln_root + 'basic\\Output\\BinDebug\\', '*.exe'])
            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign_kav', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe'])

            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Output\\BinRelease\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdm', conf.sln_root + 'basic\\Output\\BinRelease\\'])
            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdm', conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'])
            
            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Tools\\SetupScript\\res\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdm', conf.sln_root + 'basic\\Tools\\SetupScript\\res\\'])
            
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
            fileop.main(4, ['fileop.py', 'kvsign', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.exe'])
            self.update_step(14)
            
            command = 'python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign_kav', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.exe'])
            self.update_step(14)
            
            command = 'python fileop.py load_sign ' + conf.sln_root + 'basic\\KVOutput\\bindebug\\ *.dll'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'load_sign', conf.sln_root + 'basic\\KVOutput\\BinDebug\\', '*.dll'])
            command = 'python fileop.py load_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.dll'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'load_sign', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.dll'])

            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdkv', conf.sln_root + 'basic\\KVOutput\\BinRelease\\'])
            self.update_step(14)

            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdkv', conf.sln_root + 'basic\\Tools\\NSIS\\Plugins\\'])
            self.update_step(30)

            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\Tools\\KVSetupScript\\res\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdkv', conf.sln_root + 'basic\\Tools\\KVSetupScript\\res\\'])

            command = 'python sign.py bdkv ' + conf.sln_root + 'basic\\Tools\\KVNetInstall\\res\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdkv', conf.sln_root + 'basic\\Tools\\KVNetInstall\\res\\'])
            
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
            commands = []
            commands.append('python fileop.py verify_file_exist ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.*')
            commands.append('python fileop.py verify_file_version ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py verify_driver_sign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe')
            commands.append('python fileop.py verify_kav_sign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe')
            commands.append('python fileop.py verify_baidu_sign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4, ['fileop.py', 'verify_file_exist', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.*'])
            fileop.main(4, ['fileop.py', 'verify_file_version', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe,*.dll,*.sys'])
            fileop.main(4, ['fileop.py', 'verify_driver_sign', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'verify_kav_sign', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'verify_baidu_sign', conf.sln_root + 'basic\\Output\\BinRelease\\', '*.exe,*.dll,*.sys'])
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
            commands = []
            commands.append('python fileop.py kvverify_file_exist ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.*')
            commands.append('python fileop.py kvverify_file_version ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py kvverify_driver_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ .exe,*.dll,*.sys')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4, ['fileop.py', 'kvverify_file_exist', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.*'])
            fileop.main(4, ['fileop.py', 'kvverify_file_version', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '.exe,*.dll,*.sys'])
            fileop.main(4, ['fileop.py', 'kvverify_driver_sign', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'kvverify_kav_sign', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'kvverify_baidu_sign', conf.sln_root + 'basic\\KVOutput\\BinRelease\\', '*.exe,*.dll,*.sys'])
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
            except Exception, e:
                logging.error("error occers when parsing xml or run command:")
                logging.error(e)
            #first update all files in basic and accept mine if ignorefault
            if bIgnoreFault:
                command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic --accept mine-full'
                os.system(command.encode(sys.getfilesystemencoding()))
            #install
            (bInstall, bInstallMini, bInstallFull, bInstallUpdate, bInstallSilence, bInstallDefense) = getInstallOptions()
            if bInstall:
                installNormalPackage(self, 'bdm', True, bInstallSilence, bInstallDefense)
            if bInstallMini:
                installMiniPackage(self,'bdm',True,bInstallSilence, bInstallDefense)
            if (bInstall or bInstallMini) and bInstallUpdate:
                updatePackage('bdm')
                if bInstall:
                    installNormalPackage(self, 'bdm', False, bInstallSilence, bInstallDefense)
                if bInstallMini:
                    installMiniPackage(self,'bdm',False,bInstallSilence, bInstallDefense)
            #check installer
            bOk = False
            for file in os.listdir(conf.original_setup_path):
                if file[-3:] == 'exe':
                    bOk = True
                    break
            if not bOk:
                msg = ''
                if bIgnoreFault:
                    msg = 'failed to build installer, xbuild continues, please check nsis script files later'
                else:
                    msg = 'failed to build installer, please check nsis script files'
                self.report('wk-build-log', '------------------------------------------------------')
                self.report('wk-build-log', '<h5>' + msg + '</h5>')
                if not bIgnoreFault:
                    raise Exception(msg)
            command = 'xcopy /Y ' + conf.original_setup_path.replace('/', '\\') + '*.exe ' + conf.setup_path.replace('/', '\\')
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
            except Exception, e:
                logging.error("error occers when parsing xml or run command:")
                logging.error(e)
            #first update all files in basic and accept mine if ignore fault
            if bIgnoreFault:
                command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic --accept mine-full'
                os.system(command.encode(sys.getfilesystemencoding()))
            #install
            (bInstall, bInstallMini, bInstallFull, bInstallUpdate, bInstallSilence, bInstallDefense) = getInstallOptions()
            if bInstall:
                installNormalPackage(self, 'bdkv', True, bInstallSilence, bInstallDefense)
            if bInstallMini:
                installMiniPackage(self, 'bdkv', True, bInstallSilence, bInstallDefense)
            if bInstallFull:
                installKvFullPackage(self, 'bdkv', True, bInstallSilence, bInstallDefense)
            if (bInstall or bInstallMini or bInstallFull or bInstallDefense) and bInstallUpdate:
                updatePackage('bdkv')
                if bInstall:
                    installNormalPackage(self, 'bdkv', False, bInstallSilence, bInstallDefense)
                if bInstallMini:
                    installMiniPackage(self, 'bdkv', False, bInstallSilence, bInstallDefense)
                if bInstallFull:
                    installKvFullPackage(self, 'bdkv', False, bInstallSilence, bInstallDefense)
            #check installer
            bOk = False
            for file in os.listdir(conf.original_kvsetup_path):
                if file[-3:] == 'exe':
                    bOk = True
                    break
            if not bOk:
                msg = ''
                if bIgnoreFault:
                    msg = 'failed to build installer, xbuild continues, please check nsis script files later'
                else:
                    msg = 'failed to build installer, please check nsis script files'
                self.report('wk-build-log', '------------------------------------------------------')
                self.report('wk-build-log', '<h5>' + msg + '</h5>')
                if not bIgnoreFault:
                    raise Exception(msg)
            #copy exe
            command = 'xcopy /Y ' + conf.original_kvsetup_path.replace('/', '\\') + '*.exe ' + conf.kvsetup_path.replace('/', '\\')
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
            command = 'xcopy /Y ' + conf.original_setup_path.replace('/', '\\') + '*.exe ' + conf.setup_path.replace('/', '\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(1)

            command = 'python fileop.py sign ..\\output\\setup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign', '..\\output\\setup\\', '*.exe'])
            self.update_step(1)
            
            command = 'python fileop.py kvsign_kav ..\\output\\setup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign_kav', '..\\output\\setup\\', '*.exe'])
            self.update_step(1)

            command = 'python sign.py bdm ..\\output\\setup\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdm', '..\\output\\setup\\'])
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
            command = 'xcopy /Y ' + conf.original_kvsetup_path.replace('/', '\\') + '*.exe ' + conf.kvsetup_path.replace('/', '\\')
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(1)

            command = 'python fileop.py sign ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign', '..\\output\\kvsetup\\', '*.exe'])
            self.update_step(1)
            
            command = 'python fileop.py kvsign_kav ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4, ['fileop.py', 'kvsign_kav', '..\\output\\kvsetup\\', '*.exe'])
            self.update_step(1)
            
            command = 'python sign.py bdkv ..\\output\\kvsetup\\'
            self.report('wk-build-log', command)
            sign.main(3, ['sign.py', 'bdkv', '..\\output\\kvsetup\\'])
            self.update_step(1)
        BuildStep.act(self)
    
##############################################
# 0,1

class CalcInstallerMd5(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM calc installer md5"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
            #clean
            command = 'del /Q /S ' + conf.verify_md5_file
            os.system(command.encode(sys.getfilesystemencoding()))
        elif self.value == 1:
            #clean
            command = 'del /Q /S ' + conf.verify_md5_file
            os.system(command.encode(sys.getfilesystemencoding()))
            #doit
            command = 'python fileop.py md5 ..\\output\\setup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(5, ['fileop.py', 'md5', '..\\output\\setup\\', '*.exe', conf.verify_md5_file])
            
        BuildStep.act(self)
    
class KVCalcInstallerMd5(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV calc installer md5"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
            #clean
            command = 'del /Q /S ' + conf.verify_md5_file
            os.system(command.encode(sys.getfilesystemencoding()))
        elif self.value == 1:
            #clean
            command = 'del /Q /S ' + conf.verify_md5_file
            os.system(command.encode(sys.getfilesystemencoding()))
            #doit
            command = 'python fileop.py md5 ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(5, ['fileop.py', 'md5', '..\\output\\kvsetup\\', '*.exe', conf.verify_md5_file])
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
            commands.append('python fileop.py verify_driver_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py verify_kav_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py verify_baidu_sign ..\\output\\setup\\ *.exe')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4, ['fileop.py', 'verify_file_version', '..\\output\\setup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'verify_driver_sign', '..\\output\\setup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'verify_kav_sign', '..\\output\\setup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'verify_baidu_sign', '..\\output\\setup\\', '*.exe'])
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
            commands.append('python fileop.py kvverify_file_version ..\\output\\kvsetup\\ *.exe')
            commands.append('python fileop.py kvverify_driver_sign ..\\output\\kvsetup\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ..\\output\\kvsetup\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ..\\output\\kvsetup\\ *.exe')
            for item in commands:
                self.report('wk-build-log', item)
            fileop.main(4, ['fileop.py', 'kvverify_file_version', '..\\output\\kvsetup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'kvverify_driver_sign', '..\\output\\kvsetup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'kvverify_kav_sign', '..\\output\\kvsetup\\', '*.exe'])
            fileop.main(4, ['fileop.py', 'kvverify_baidu_sign', '..\\output\\kvsetup\\', '*.exe'])
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
            cmd = 'net use ' + comm.getArchiveRoot('bdm')
            commands.append(cmd)
            commands.append('python send.py bdm daily')
            for item in commands:
                self.report('wk-build-log', item)
            os.system(cmd.encode(sys.getfilesystemencoding()))
            send.main(3, ['send.py', 'bdm', 'daily'])
        elif self.value == 2:
            commands = []
            cmd = 'net use ' + comm.getArchiveRoot('bdm')
            commands.append(cmd)
            commands.append('python send.py bdm version')
            for item in commands:
                self.report('wk-build-log', item)
            os.system(cmd.encode(sys.getfilesystemencoding()))
            send.main(3, ['send.py', 'bdm', 'version'])
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
            cmd = 'net use ' + comm.getArchiveRoot('bdkv')
            commands.append(cmd)
            commands.append('python send.py bdkv daily')
            for item in commands:
                self.report('wk-build-log', item)
            os.system(cmd.encode(sys.getfilesystemencoding()))
            send.main(3, ['send.py', 'bdkv', 'daily'])
        elif self.value == 2:
            commands = []
            cmd = 'net use ' + comm.getArchiveRoot('bdkv')
            commands.append(cmd)
            commands.append('python send.py bdkv version')
            for item in commands:
                self.report('wk-build-log', item)
            os.system(cmd.encode(sys.getfilesystemencoding()))
            send.main(3, ['send.py', 'bdkv', 'version'])
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
            command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic --accept mine-full'
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(5)
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command.replace('bCRjzYKzk', 'XXXXXX'))
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
            command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic --accept mine-full'
            self.report('wk-build-log', command.replace('bCRjzYKzk', 'XXXXXX'))
            os.system(command.encode(sys.getfilesystemencoding()))
            self.update_step(5)
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command.replace('bCRjzYKzk', 'XXXXXX'))
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
            commands = getMarkupCodeCommands('bdm', self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No markup code commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            commands = getMarkupCodeCommands('bdkv', self.value)
            if len(commands) == 0:
                self.report('wk-build-log', 'No markup code commands')
            else:
                for item in commands:
                    self.report('wk-build-log', item.replace('bCRjzYKzk', 'XXXXXX'))
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
            commands = genSvnLockActions('bdm', 'unlock', self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('bCRjzYKzk','XXXXXX'))
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
            commands = genSvnLockActions('bdkv', 'unlock', self.value)
            for item in commands:
                #self.report('wk-build-log', item.replace('bCRjzYKzk','XXXXXX'))
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
            genMailMsg('bdm')
            command = '..\\bin\\blat.exe -install proxy-in.baidu.com liuheng@baidu.com 3 25'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            command = '..\\bin\\blat.exe "' + conf.bdm_mail_file + '" -to zhangkai06@baidu.com,niekefeng@baidu.com,wuguangzhu@baidu.com,yishanhong@baidu.com,zhaoxin05@baidu.com,caoyang@baidu.com,zhangjing11@baidu.com,zhangwei21@baidu.com,weiguangjun@baidu.com,yangchuanyi01@baidu.com,liying12@baidu.com,tongyang@baidu.com,zhaobeining@baidu.com,liuheng@baidu.com -subject "[DailyBuild][Baiduan][%date%]"'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
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
            genMailMsg('bdkv')
            command = '..\\bin\\blat.exe -install proxy-in.baidu.com liuheng@baidu.com 3 25'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
            command = '..\\bin\\blat.exe "' + conf.bdkv_mail_file + '" -to mengqiyuan@baidu.com,caoyang@baidu.com,wuguangzhu@baidu.com,zhoujiwen@baidu.com,zhaoxin05@baidu.com,wumengqing@baidu.com,tongyang@baidu.com,gaoguanghai@baidu.com,xulin01@baidu.com,lianlian@baidu.com,liuheng@baidu.com -subject "[DailyBuild][Baidusd][%date%]"'
            self.report('wk-build-log', command)
            os.system(command.encode(sys.getfilesystemencoding()))
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
