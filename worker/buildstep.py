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
                      'postbuild':'PostBuild',
                      }
kvbuild_step_creator = {
                      'prebuild':'KVPreBuild',
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
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD " + conf.sln_root + dir
                commands.append(command)
                break
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    if svnAction == 'update':
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD " + conf.sln_root + "basic")
        commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD " + conf.sln_root + "stable_proj")
    elif svnAction == 'checkout':
        commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "basic_proj" + codeDir + " " + conf.sln_root + "basic")
        if codeDir.find('branches') != -1 or codeDir.find('tags') != -1 or revision != 'HEAD':
            commands.append("svn checkout --non-interactive --no-auth-cache --username buildbot --password 123456 --revision " + revision + " " + conf.svn_url + "stable_proj" + codeDir + " " + conf.sln_root + "stable_proj")
        else:
            commands.append("svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD " + conf.sln_root + "stable_proj")
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
        vcbuildAction = ''
    
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
                command = "vcbuild " + vcbuildAction + " /time /M16 /errfile:" + errDir + item + logName + ".log " + conf.sln_root \
                 + dir + "\\Projects\\" + item + ".sln \"" + type + "\""
                commands.append(command)
            writer = open(confFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
    return commands
    
def makeBinplace(product,files):
    if product == 'bdm':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Full -r ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\ -:DEST BDM ' + conf.sln_root + files
    elif product == 'bdkv':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Full -r ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ' + conf.sln_root + files

def genSymbols(product):
    commands = []
    if product == 'bdm':
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\*.exe'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\FTSOManager\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\FTSWManager\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\bdkv\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmhomepageplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmmainframeplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmsomanagerplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmswmanagerplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmtrayplugins\\*.dll'))
        commands.append(makeBinplace('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\wsplugins\\*.dll'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Full\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Stripped\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDM"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
    elif product == 'bdkv':
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.exe'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\bdmantivirus\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\bdmsysrepair\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\drivers\\*.sys'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\bdkv\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\bdkvtrayplugins\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.exe'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.exe'))
        commands.append(makeBinplace('bdkv','basic\\KVOutput\\BinRelease\\*.exe'))
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Full\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Stripped\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDKV"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ' + conf.sln_root + 'stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
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
                os.system(item)
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
                os.system(item)
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
                        os.system(command)
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item)
                    else:
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item)
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
                        os.system(command)
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item)
                    else:
                        self.report('wk-build-log', item.replace('123456','XXXXXX'))
                        os.system(item)
                    self.update_step(3)
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
                    os.system(item)
            BuildStep.act(self)
            bErr = False
            for file in os.listdir(conf.log_path):
                if file[-3:] == 'log':
                    errLog = comm.getMsg(conf.log_path + file)
                    if errLog != '':
                        bErr = True
                        break
            if bErr:
                msg = 'Build error(s) found, xbuild quit, please handler these error(s) below : '
                self.report('wk-status-change', 'error')
                self.report('wk-build-log',msg)
                for file in os.listdir(conf.log_path):
                    if file[-3:] == 'log':
                        errLog = comm.getMsg(conf.log_path + file)
                        if errLog != '':
                            self.report('wk-build-log','<h5>------------------------------------------------------------------------------------------------------------</h5>')
                            self.report('wk-build-log','<h5>' + file + '</h5>')
                            self.report('wk-build-log',errLog)
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
                    os.system(item)
            BuildStep.act(self)
            bErr = False
            for file in os.listdir(conf.kvlog_path):
                if file[-3:] == 'log':
                    errLog = comm.getMsg(conf.kvlog_path + file)
                    if errLog != '':
                        bErr = True
                        break
            if bErr:
                msg = 'Build error(s) found, xbuild quit, please handler these error(s) below : '
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
                            for line in lines:
                                self.report('wk-build-log',line)
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
            os.system(command)
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
            os.system(command)
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
            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Output\\BinRelease\\'
            self.report('wk-build-log', command)
            sign.main(3,['sign.py','bdm',conf.sln_root + 'basic\\Output\\BinRelease\\'])
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
            os.system('del /Q ' + conf.verify_log_file)
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
            os.system('del /Q ' + conf.kvverify_log_file)
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
            command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ' + conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
            self.report('wk-build-log', command)
            os.system(command)
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
            os.system(command)
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
            command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
            self.report('wk-build-log', command)
            os.system(command)
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
            command = 'xcopy /Y ' + conf.original_kvsetup_path.replace('/','\\') + '*.exe ' + conf.kvsetup_path.replace('/','\\')
            self.report('wk-build-log', command)
            os.system(command)
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
            os.system(command)
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
            os.system(command)
            self.update_step(1)

            command = 'python fileop.py sign ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','kvsign','..\\output\\kvsetup\\','*.exe'])
            self.update_step(1)
            
            command = 'python fileop.py sign_kav ..\\output\\kvsetup\\ *.exe'
            self.report('wk-build-log', command)
            fileop.main(4,['fileop.py','sign_kav','..\\output\\kvsetup\\','*.exe'])
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
                self.update_step(2)
                os.system(item)
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
                self.update_step(2)
                os.system(item)
        BuildStep.act(self)
    
##############################################
# 0,1

class Commit(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM Committing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command)
            os.system(command)
        BuildStep.act(self)
    
class KVCommit(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV Committing files"
    
    def act(self):
        if self.value == 0:
            self.report('wk-build-log', 'Passed')
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            self.report('wk-build-log', command)
            os.system(command)
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
