# coding=UTF-8
"""
@author    tomas
@date    2013-03-07
@desc
    express build mode class library
"""

import sys,os,conf,xml.dom.minidom,datetime,comm
import rewrite_version,sign,fileop,send
import logging

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
        logging.info(e)
        print e
    
    return slns
    
def getSvnCommands(product, value):
    svnAction = 'update'
    if value == 2 or value == 4:
        svnAction = 'update'
    elif value == 1 or value == 3:
        svnAction = 'checkout'
    
    bForce = False
    if value == 1 or value == 2:
        bForce = True
    elif value == 3 or value == 4:
        bForce = False

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
                svnDir = dir + '/trunk'
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.getAttribute('build') != '1' and (not bForce):
                    continue
                if node.getAttribute('product') != '' and node.getAttribute('product') != product:
                    continue
                if svnAction == 'checkout':
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD http://192.168.10.242:8000/client/"  + svnDir + conf.sln_root + dir
                elif svnAction == 'update':
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD " + conf.sln_root + dir
                commands.append(command)
                break
        except Exception,e:
            logging.info("error occers when parsing xml or run command:")
            logging.info(e)
            print "error occers when parsing xml or run command:"
            print e
    commands = list(set(commands))
    return commands

def getBuildCommands(product,value):
    checklogFile = ''
    errDir = ''
    if product == 'bdm':
        checklogFile = conf.checklog_file
        errDir = 'err\\'
    elif product == 'bdkv':
        checklogFile = conf.kvchecklog_file
        errDir = 'kverr\\'

    vcbuildAction = ''
    if value == 1 or value == 3:
        vcbuildAction = '/rebuild'
    elif value == 2 or value == 4:
        vcbuildAction = ''
    
    bForce = False
    if value == 1 or value == 2:
        bForce = True
    elif value == 3 or value == 4:
        bForce = False
    
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
                svnDir = dir + '/trunk'
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.getAttribute('build') != '1' and (not bForce):
                    continue
                if node.getAttribute('product') != '' and node.getAttribute('product') != product:
                    continue
                node.setAttribute('build','0')
                type = node.getAttribute('type')
                logName = ''
                if type.lower().find('release') != -1:
                    logName = 'Release'
                else:
                    continue
                command = "vcbuild " + vcbuildAction + " /time /M16 /errfile:..\\output\\" + errDir + item + logName + ".log " + conf.sln_root \
                 + dir + "\\Projects\\" + item + ".sln \"" + type + "\""
                commands.append(command)
            writer = open(confFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.info("error occers when parsing xml or run command:")
            logging.info(e)
            print "error occers when parsing xml or run command:"
            print e
    return commands
    
def makeBinplace(product,files):
    if product == 'bdm':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\Full -r ' + conf.sln_root + 'basic\\Output\\Symbols\\Release\\ -:DEST BDM ' + conf.sln_root + files
    elif product == 'bdkv':
        return conf.byp_bin_path + 'binplace.exe -e -a -x -s .\\Stripped -n ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\Full -r ' + conf.sln_root + 'basic\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ' + conf.sln_root + files

def genSymbols(product):
    commands = []
    if product == 'bdm':
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\*.exe'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\FTSOManager\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\FTSWManager\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\bdkv\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmhomepageplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmmainframeplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmsomanagerplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmswmanagerplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\bdmtrayplugins\\*.dll'))
        commands.append(makeBinpalce('bdm',conf.sln_root + 'basic\\Output\\BinRelease\\plugins\\wsplugins\\*.dll'))
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
            commands.append('del /Q ..\\output\\setup\\*.exe')
            commands.append('del /Q ..\\output\\err\\*.log')
        elif product == 'bdkv':
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\AutoBuild\\kvversionbuildid.txt')
            commands.append('del /Q ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi')
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
            pass
        elif self.para[0] == 'wk-build-log':
            sid = self.para[1]
            ws = self.para[2]
            #整饰特殊字符
            msg = msg.replace('"',' ')
            if msg[-1] == '\\':
                msg = msg[0:-1] #python bug maybe
            logging.info('sid : %s, msrc : %s, buildlog : %s' % (sid, msrc, msg))
            ws.send('{"msrc":"%s","content":"%s"}' % (msrc, msg))
    
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
             logging.info('Passed')
        else:
            commands = genPrebuildActions('bdm',self.value)
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
                os.system(item)
        BuildStep.act(self)
    
class KVPreBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV prebuild operations"
    
    def act(self):
        if self.value == 0:
             logging.info('Passed')
        else:
            commands = genPrebuildActions('bdkv',self.value)
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
                os.system(item)
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
            logging.info('Passed')
        else:
            commands = getSvnCommands('bdm',self.value)
            if len(commands) == 0:
                logging.info("No svn commands")
            else:
                for item in commands:
                    logging.info(item)
                    self.report('wk-build-log', item)
                    self.update_step(3)
                    os.system(item)
        BuildStep.act(self)
    
class KVSvn(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV svn operations"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        else:
            commands = getSvnCommands('bdkv',self.value)
            if len(commands) == 0:
                logging.info("No svn commands")
            else:
                for item in commands:
                    logging.info(item)
                    self.report('wk-build-log', item)
                    self.update_step(3)
                    os.system(item)
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
            logging.info('Passed')
        elif self.value == 1:
            command = 'python rewrite_version.py bdm daily'
            logging.info(command)
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdm','daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdm version'
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            command = 'python rewrite_version.py bdkv daily'
            logging.info(command)
            self.report('wk-build-log', command)
            rewrite_version.main(3,['rewrite_version.py','bdkv','daily'])
        elif self.value == 2:
            command = 'python rewrite_version.py bdkv version'
            logging.info(command)
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
            logging.info('Passed')
        else:
            commands = getBuildCommands('bdm',self.value)
            if len(commands) == 0:
                logging.info("No build commands")
            else:
                for item in commands:
                    logging.info(item)
                    self.report('wk-build-log', item)
                    self.update_step(10)
                    #os.system(item)
        BuildStep.act(self)
        for file in os.listdir(conf.log_path):
            if file[-3:] == 'log' and comm.getMsg('../output/err/'+file) != '':
                print '\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a'
                msg = 'Build error(s) found, xbuild quit, please check ../output/err for build log(s).'
                logging.info(msg)
                self.report('wk-build-error', msg)
                raise msg
            
    
class KVBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV compiling and building"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        else:
            commands = getBuildCommands('bdkv',self.value)
            if len(commands) == 0:
                logging.info("No build commands")
            else:
                for item in commands:
                    logging.info(item)
                    self.report('wk-build-log', item)
                    self.update_step(10)
                    #os.system(item)
        BuildStep.act(self)
        for file in os.listdir(conf.kvlog_path):
            if file[-3:] == 'log' and comm.getMsg('../output/kverr/'+file) != '':
                print '\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a'
                logging.info('Build error(s) found, xbuild quit, please check ../output/kverr for build log(s).')
                raise 'Build error(s) found, xbuild quit, please check ../output/kverr for build log(s).'
    
##############################################
# 0,1

class Pack(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDM packing resources"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        elif self.value == 1:
            command = 'cscript pack.vbs bdm'
            logging.info(command)
            os.system(command)
        BuildStep.act(self)
    
class KVPack(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV packing resources"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        elif self.value == 1:
            command = 'cscript pack.vbs bdkv'
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            command = 'python sign.py bdm ' + conf.sln_root + 'basic\\Output\\BinRelease\\'
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py kvsign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvsign_kav ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python sign.py bdkv ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            fileop.main(4,['fileop.py','kvsign',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            self.update_step(20)
            fileop.main(4,['fileop.py','kvsign_kav',conf.sln_root + 'basic\\KVOutput\\BinRelease\\','*.exe'])
            self.update_step(60)
            sign.main(3,['sign.py','bdkv',conf.sln_root + 'basic\\KVOutput\\BinRelease\\'])
            self.update_step(100)
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
            logging.info('Passed')
        elif self.value == 1:
            os.system('del /Q ' + conf.verify_log_file)
            commands = []
            commands.append('python fileop.py verify_file_exist ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.*')
            commands.append('python fileop.py verify_file_version ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py verify_baidu_sign ' + conf.sln_root + 'basic\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            for item in commands:
                logging.info(item)
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
            logging.info('Passed')
        elif self.value == 1:
            os.system('del /Q ' + conf.kvverify_log_file)
            commands = []
            commands.append('python fileop.py kvverify_file_exist ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.*')
            commands.append('python fileop.py kvverify_file_version ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python fileop.py kvverify_driver_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ' + conf.sln_root + 'basic\\KVOutput\\BinRelease\\ .exe,*.dll,*.sys')
            for item in commands:
                logging.info(item)
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
            logging.info('Passed')
        elif self.value == 1:
            command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ' + conf.sln_root + 'basic\\tools\\SetupScript\\BDM_setup.nsi'
            logging.info(command)
            self.report('wk-build-log', command)
            os.system(command)
            command = 'xcopy ' + conf.original_setup_path.replace('/','\\') + '*.exe ' + conf.setup_path.replace('/','\\')
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            command = conf.sln_root + 'basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ' + conf.sln_root + 'basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
            logging.info(command)
            self.report('wk-build-log', command)
            os.system(command)
            command = 'xcopy ' + conf.original_kvsetup_path.replace('/','\\') + '*.exe ' + conf.kvsetup_path.replace('/','\\')
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            command = 'python sign.py bdm .\\output\\setup\\'
            logging.info(command)
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
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py sign ..\\output\\kvsetup\\ *.exe')
            commands.append('python fileop.py sign_kav ..\\output\\kvsetup\\ *.exe')
            commands.append('python sign.py bdkv ..\\output\\kvsetup\\')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            fileop.main(4,['fileop.py','sign','..\\output\\kvsetup\\','*.exe'])
            self.update_step(1)
            fileop.main(4,['fileop.py','sign_kav','..\\output\\kvsetup\\','*.exe'])
            self.update_step(3)
            sign.main(3,['sign.py','bdkv','..\\output\\kvsetup\\'])
            self.update_step(5)
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
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py verify_file_version ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py verify_baidu_sign ..\\output\\setup\\ *.exe')
            for item in commands:
                logging.info(item)
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
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('python fileop.py kvverify_file_version ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_driver_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_kav_sign ..\\output\\setup\\ *.exe')
            commands.append('python fileop.py kvverify_baidu_sign ..\\output\\setup\\ *.exe')
            for item in commands:
                logging.info(item)
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
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdm daily')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            #send.main(3,['send.py','bdm','daily'])
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdm version')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            #send.main(3,['send.py','bdm','version'])
        BuildStep.act(self)
    
class KVSend(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV sending files to archive folder"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdkv daily')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            #send.main(3,['send.py','bdkv','daily'])
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python send.py bdkv version')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
            #send.main(3,['send.py','bdkv','version'])
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
            logging.info('Passed')
        elif self.value == 1:
            commands = genSymbols('bdm')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
                self.update_step(3)
                #os.system(item)
        BuildStep.act(self)
    
class KVSymAdd(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV collecting symbols to symbol server"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        elif self.value == 1:
            commands = genSymbols('bdkv')
            for item in commands:
                logging.info(item)
                self.report('wk-build-log', item)
                self.update_step(3)
                #os.system(item)
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
            logging.info('Passed')
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            logging.info(command)
            self.report('wk-build-log', command)
            #os.system(command)
        BuildStep.act(self)
    
class KVCommit(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV Committing files"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ' + conf.sln_root + 'basic -m "%s" --no-unlock' % msg
            logging.info(command)
            self.report('wk-build-log', command)
            #os.system(command)
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
            logging.info('Passed')
        BuildStep.act(self)
    
class KVPostBuild(BuildStep):
    def __init__(self, n, v, o, w, p):
        BuildStep.__init__(self, n, v, o, w, p)
    
    def __str__(self):
        return "BDKV postbuild operations"
    
    def act(self):
        if self.value == 0:
            logging.info('Passed')
        BuildStep.act(self)
    
##############################################
