"""
@author    tomas
@date    2013-03-07
@desc
    express build mode class library
"""

import sys,os,conf,xml.dom.minidom,datetime,comm
import rewrite_version,sign,fileop,send

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
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD http://192.168.10.242:8000/client/"  + svnDir + " ..\\..\\" + dir
                elif svnAction == 'update':
                    command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD ..\\..\\" + dir
                commands.append(command)
                break
        except Exception,e:
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
                command = "vcbuild " + vcbuildAction + " /time /M16 /errfile:AutoBuild\\" + errDir + item + logName + ".log ..\\..\\" \
                 + dir + "\\Projects\\" + item + ".sln \"" + type + "\""
                commands.append(command)
            writer = open(confFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            print "error occers when parsing xml or run command:"
            print e
    return commands
    
def genSymbols(product):
    commands = []
    if product == 'bdm':
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\*.exe')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\FTSOManager\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\FTSWManager\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\bdkv\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdmhomepageplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdmmainframeplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdmsomanagerplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdmswmanagerplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\bdmtrayplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\Output\\Symbols\\Release\\Full -r ..\\Output\\Symbols\\Release\\ -:DEST BDM ..\\Output\\BinRelease\\plugins\\wsplugins\\*.dll')
        commands.append('symstore add /r /f ..\\Output\\Symbols\\Release\\Full\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDM"')
        commands.append('symstore add /r /f ..\\Output\\Symbols\\Release\\Stripped\\BDM\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDM"')
        commands.append('symstore add /r /f ..\\..\\stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ..\\..\\stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
    elif product == 'bdkv':
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\*.exe')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\bdmantivirus\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\bdmsysrepair\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\drivers\\*.sys')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\plugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\plugins\\bdkv\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\plugins\\bdkvtrayplugins\\*.dll')
        commands.append('.\\AutoBuild\\binplace.exe -e -a -x -s .\\Stripped -n ..\\KVOutput\\Symbols\\Release\\Full -r ..\\KVOutput\\Symbols\\Release\\ -:DEST BDKV ..\\KVOutput\\BinRelease\\plugins\\bdkvrtpplugins\\*.dll')
        commands.append('symstore add /r /f ..\\KVOutput\\Symbols\\Release\\Full\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "BDKV"')
        commands.append('symstore add /r /f ..\\KVOutput\\Symbols\\Release\\Stripped\\BDKV\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "BDKV"')
        commands.append('symstore add /r /f ..\\..\\stable_proj\\Symbols\\Full\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Full\\Release /t "THIRD"')
        commands.append('symstore add /r /f ..\\..\\stable_proj\\Symbols\\Stripped\\Release\\*.pdb /s \\\\192.168.10.242\\public\\Symbols\\Stripped\\Release /t "THIRD"')
    return commands

def genPrebuildActions(product,value):
    commands = []
    if value == 1 or value == 2:
        commands.append('del /Q ..\\include\\CommonInclude\\BDMVersion.h')
        commands.append('del /Q ..\\include\\CommonInclude\\BuildVer.h')
        if product == 'bdm':
            commands.append('del /Q AutoBuild\\buildid.txt')
            commands.append('del /Q AutoBuild\\versionbuildid.txt')
            commands.append('del /Q SetupScript\\BDM_setup.nsi')
            commands.append('del /Q /S .\\setup')
            commands.append('del /Q /S .\\AutoBuild\\err')
        elif product == 'bdkv':
            commands.append('del /Q AutoBuild\\kvbuildid.txt')
            commands.append('del /Q AutoBuild\\kvversionbuildid.txt')
            commands.append('del /Q KVSetupScript\\BDKV_setup.nsi')
            commands.append('del /Q /S .\\kvsetup')
            commands.append('del /Q /S .\\AutoBuild\\kverr')
    if value == 2:
        commands.append('del /Q /S ..\\lib')
        if product == 'bdm':
            commands.append('del /Q /S ..\\Output')
        elif product == 'bdkv':
            commands.append('del /Q /S ..\\KVOutput')
    commands.append('svn update --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD ..\\..\\basic')
    return commands

##############################################

class BuildStep:
    def __init__(self,n,v,o):
        self.name = n
        self.value = v
        self.order = o
    
    def __str__(self):
        #return 'name=%s value=%s order=%d' % (self.name,self.value,self.order)
        pass
    
    def act(self):
        pass

##############################################
# 0

class PreBuild(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM prebuild operations"
    
    def act(self):
        if self.value == 0:
             print 'Passed'
        else:
            commands = genPrebuildActions('bdm',self.value)
            for item in commands:
                print item
                os.system(item)
    
class KVPreBuild(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV prebuild operations"
    
    def act(self):
        if self.value == 0:
             print 'Passed'
        else:
            commands = genPrebuildActions('bdkv',self.value)
            for item in commands:
                print item
                os.system(item)
    
##############################################
# 0,1,2,3,4

class Svn(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM svn operations"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        else:
            commands = getSvnCommands('bdm',self.value)
            if len(commands) == 0:
                print "No svn commands"
            else:
                for item in commands:
                    print item
                    os.system(item)
    
class KVSvn(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV svn operations"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        else:
            commands = getSvnCommands('bdkv',self.value)
            if len(commands) == 0:
                print "No svn commands"
            else:
                for item in commands:
                    print item
                    os.system(item)
    
##############################################
# 0,1,2

class RewriteVersion(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM update build version and resource definition"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'python AutoBuild\\rewrite_version.py bdm daily'
            print command
            rewrite_version.main(3,['rewrite_version.py','bdm','daily'])
        elif self.value == 2:
            command = 'python AutoBuild\\rewrite_version.py bdm version'
            print command
            rewrite_version.main(3,['rewrite_version.py','bdm','version'])

    
class KVRewriteVersion(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV update build version and resource definition"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'python AutoBuild\\rewrite_version.py bdkv daily'
            print command
            rewrite_version.main(3,['rewrite_version.py','bdkv','daily'])
        elif self.value == 2:
            command = 'python AutoBuild\\rewrite_version.py bdkv version'
            print command
            rewrite_version.main(3,['rewrite_version.py','bdkv','version'])
    
##############################################
# 0,1,2

class Build(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM compiling and building"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        else:
            commands = getBuildCommands('bdm',self.value)
            if len(commands) == 0:
                print "No build commands"
            else:
                for item in commands:
                    print item
                    os.system(item)
        for file in os.listdir('./AutoBuild/err'):
            if comm.getMsg('./AutoBuild/err/'+file) != '':
                print '\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a'
                raise 'Build error(s) found, xbuild quit, please check AutoBuild/err for build log(s).'
            
    
class KVBuild(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV compiling and building"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        else:
            commands = getBuildCommands('bdkv',self.value)
            if len(commands) == 0:
                print "No build commands"
            else:
                for item in commands:
                    print item
                    os.system(item)
        for file in os.listdir('./AutoBuild/kverr'):
            if comm.getMsg('./AutoBuild/kverr/'+file) != '':
                print '\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a'
                raise 'Build error(s) found, xbuild quit, please check AutoBuild/kverr for build log(s).'
    
##############################################
# 0,1

class Pack(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM packing resources"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'cscript AutoBuild\\pack.vbs bdm'
            print command
            os.system(command)
    
class KVPack(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV packing resources"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'cscript AutoBuild\\pack.vbs bdkv'
            print command
            os.system(command)
    
##############################################
# 0,1

class Sign(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM signning files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'python AutoBuild\\sign.py bdm ..\\Output\\BinRelease\\'
            print command
            sign.main(3,['sign.py','bdm','..\\Output\\BinRelease\\'])
    
class KVSign(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV signning files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            commands.append('python AutoBuild\\fileop.py kvsign ..\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvsign_kav ..\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python AutoBuild\\sign.py bdkv ..\\KVOutput\\BinRelease\\')
            for item in commands:
                print item
            fileop.main(4,['fileop.py','kvsign','..\\KVOutput\\BinRelease\\','*.exe'])
            fileop.main(4,['fileop.py','kvsign_kav','..\\KVOutput\\BinRelease\\','*.exe'])
            sign.main(3,['sign.py','bdkv','..\\KVOutput\\BinRelease\\'])
    
##############################################
# 0,1

class Verify(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM verifing files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            os.system('del /Q AutoBuild\\BinVerify.txt')
            commands = []
            commands.append('python AutoBuild\\fileop.py verify_file_exist ..\\Output\\BinRelease\\ *.*')
            #commands.append('python AutoBuild\\fileop.py verify_file_version ..\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python AutoBuild\\fileop.py verify_baidu_sign ..\\Output\\BinRelease\\ *.exe,*.dll,*.sys')
            for item in commands:
                print item
            fileop.main(4,['fileop.py','verify_file_exist','..\\Output\\BinRelease\\','*.*'])
            #fileop.main(4,['fileop.py','verify_file_version','..\\Output\\BinRelease\\','*.exe,*.dll,*.sys'])
            fileop.main(4,['fileop.py','verify_baidu_sign','..\\Output\\BinRelease\\','*.exe,*.dll,*.sys'])
    
class KVVerify(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV verifing files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            os.system('del /Q AutoBuild\\KVBinVerify.txt')
            commands = []
            commands.append('python AutoBuild\\fileop.py kvverify_file_exist ..\\KVOutput\\BinRelease\\ *.*')
            #commands.append('python AutoBuild\\fileop.py kvverify_file_version ..\\KVOutput\\BinRelease\\ *.exe,*.dll,*.sys')
            commands.append('python AutoBuild\\fileop.py kvverify_driver_sign ..\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvverify_kav_sign ..\\KVOutput\\BinRelease\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvverify_baidu_sign ..\\KVOutput\\BinRelease\\ .exe,*.dll,*.sys')
            for item in commands:
                print item
            fileop.main(4,['fileop.py','kvverify_file_exist','..\\KVOutput\\BinRelease\\','*.*'])
            #fileop.main(4,['fileop.py','kvverify_file_version','..\\KVOutput\\BinRelease\\','.exe,*.dll,*.sys'])
            fileop.main(4,['fileop.py','kvverify_driver_sign','..\\KVOutput\\BinRelease\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_kav_sign','..\\KVOutput\\BinRelease\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_baidu_sign','..\\KVOutput\\BinRelease\\','*.exe,*.dll,*.sys'])

##############################################
# 0,1

class Install(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM building installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = '..\\..\\basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ..\\..\\basic\\tools\\SetupScript\\BDM_setup.nsi'
            print command
            os.system(command)
    
class KVInstall(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV building installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = '..\\..\\basic\\tools\\NSIS\\makensis.exe /X"SetCompressor /FINAL lzma" ..\\..\\basic\\tools\\KVSetupScript\\BDKV_setup.nsi'
            print command
            os.system(command)
    
##############################################
# 0,1

class SignInstaller(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM signning installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            command = 'python AutoBuild\\sign.py bdm .\\setup\\'
            print command
            sign.main(3,['sign.py','bdm','.\\setup\\'])
    
class KVSignInstaller(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV signning installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            commands.append('python AutoBuild\\fileop.py sign .\\kvsetup\\ *.exe')
            commands.append('python AutoBuild\\fileop.py sign_kav .\\kvsetup\\ *.exe')
            commands.append('python AutoBuild\\sign.py bdkv .\\kvsetup\\')
            for item in commands:
                print item
            fileop.main(4,['fileop.py','sign','.\\kvsetup\\','*.exe'])
            fileop.main(4,['fileop.py','sign_kav','.\\kvsetup\\','*.exe'])
            sign.main(3,['sign.py','bdkv','.\\kvsetup\\'])
    
##############################################
# 0,1

class VerifyInstaller(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM verifing installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            #commands.append('python AutoBuild\\fileop.py verify_file_version .\\setup\\ *.exe')
            commands.append('python AutoBuild\\fileop.py verify_baidu_sign .\\setup\\ *.exe')
            for item in commands:
                print item
            #fileop.main(4,['fileop.py','verify_file_version','.\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','verify_baidu_sign','.\\setup\\','*.exe'])
    
class KVVerifyInstaller(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV verifing installer"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            #commands.append('python AutoBuild\\fileop.py kvverify_file_version .\\setup\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvverify_driver_sign .\\setup\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvverify_kav_sign .\\setup\\ *.exe')
            commands.append('python AutoBuild\\fileop.py kvverify_baidu_sign .\\setup\\ *.exe')
            for item in commands:
                print item
            #fileop.main(4,['fileop.py','kvverify_file_version','.\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_driver_sign','.\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_kav_sign','.\\setup\\','*.exe'])
            fileop.main(4,['fileop.py','kvverify_baidu_sign','.\\setup\\','*.exe'])

##############################################
# 0,1

class Send(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM sending files to archive folder"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python AutoBuild\\send.py bdm daily')
            for item in commands:
                print item
            send.main(3,['send.py','bdm','daily'])
            
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python AutoBuild\\send.py bdm version')
            for item in commands:
                print item
            send.main(3,['send.py','bdm','version'])
    
class KVSend(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV sending files to archive folder"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python AutoBuild\\send.py bdkv daily')
            for item in commands:
                print item
            send.main(3,['send.py','bdkv','daily'])
        elif self.value == 2:
            commands = []
            commands.append('net use \\\\192.168.10.242\\public')
            commands.append('python AutoBuild\\send.py bdkv version')
            for item in commands:
                print item
            send.main(3,['send.py','bdkv','version'])
    
##############################################
# 0,1

class SymAdd(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM collecting symbols to symbol server"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = genSymbols('bdm')
            for item in commands:
                print item
                os.system(item)
    
class KVSymAdd(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV collecting symbols to symbol server"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            commands = genSymbols('bdkv')
            for item in commands:
                print item
                os.system(item)
    
##############################################
# 0,1

class Commit(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM Committing files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ..\\..\\Basic -m "%s" --no-unlock' % msg
            print command
            os.system(command)
    
class KVCommit(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV Committing files"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
        elif self.value == 1:
            msg = 'xbuild commit %s' % datetime.datetime.now()
            command = 'svn commit ..\\..\\Basic -m "%s" --no-unlock' % msg
            print command
            os.system(command)
    
##############################################
# 0,1

class PostBuild(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDM postbuild operations"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
    
class KVPostBuild(BuildStep):
    def __init__(self, n, v, o):
        BuildStep.__init__(self, n, v, o)
    
    def __str__(self):
        return "BDKV postbuild operations"
    
    def act(self):
        if self.value == 0:
            print 'Passed'
    
##############################################
