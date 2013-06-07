# coding=UTF-8
"""
@author    thomas
@date    2013-03-07
@desc
    express build mode,usage : python xbuild.py <nickname>
"""

import sys,os,conf,xml.dom.minidom,buildstep,new
import threading
import logging
import time

#worker thread
class Worker(threading.Thread):
    def __init__(self, ws, sid, evt):
        self.socket = ws
        self.id = sid
        self.evt = evt
        threading.Thread.__init__(self)
    
    def setInitParam(self, msg):
        ctx = msg['content']
        settings = ctx.split('|')
        self.projName = ''
        if settings[1] == 'X光':
            self.projName = 'bdkv'
        elif settings[1] == '极光':
            self.projName = 'bdm'
        self.slns = {}
        for item in settings[2].split(';'):
            slnName = item[0:item.find(',')]
            slnBuild = item[item.find(',')+1:]
            self.slns[slnName] = slnBuild
        self.options = {}
        for item in settings[3].split(';'):
            opName = item[0:item.find(',')]
            opVal = item[item.find(',')+1:]
            self.options[opName] = opVal
        self.extraOptions = {}
        iIndex = 0
        for i in range(4,len(settings)):
            iIndex = settings[i].find(',')
            self.extraOptions[settings[i][0:iIndex]] = settings[i][iIndex+1:]
        
        self.applyBuildSettings()
        
    def applySlnSettings(self):
        projConf = {}
        if self.projName == 'bdkv':
            projConf = conf.bdkv_conf_files
        elif self.projName == 'bdm':
            projConf = conf.bdm_conf_files
            
        try:
            for key,val in self.slns.items():
                confFile = './buildswitch/' + projConf[key] + '.xml'
                dom = xml.dom.minidom.parse(confFile)
                root = dom.documentElement
                for node in root.childNodes:
                    if node.nodeType != node.ELEMENT_NODE:
                        continue
                    product = node.getAttribute('product')
                    if product != '' and product != self.projName:
                        node.setAttribute('build','0')
                        continue
                    elif val == '0':
                        node.setAttribute('build','0')
                        continue
                    type = node.getAttribute('type')
                    if type.lower().find('debug') != -1:
                        if self.options['buildtype'] == '1' or self.options['buildtype'] == '3':
                            node.setAttribute('build','1')
                        else:
                            node.setAttribute('build','0')
                    elif type.lower().find('release') != -1:
                        if self.options['buildtype'] == '2' or self.options['buildtype'] == '3':
                            node.setAttribute('build','1')
                        else:
                            node.setAttribute('build','0')
                writer = open(confFile,'w')
                dom.writexml(writer)
                writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
        
    def applyBuildOptions(self):
        bsFile = './buildswitch/buildstep.xml'
        try:
            dom = xml.dom.minidom.parse(bsFile)
            root = dom.documentElement
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                product = node.getAttribute('product')
                if product != self.projName:
                    continue;
                else:
                    for step in node.childNodes:
                        if step.nodeType != step.ELEMENT_NODE:
                            continue
                        name = step.getAttribute('name')
                        if self.options.has_key(name):
                            step.setAttribute('value',self.options[name])
                        elif self.extraOptions.has_key(name):
                            step.setAttribute('value',self.extraOptions[name])
                        else:
                            step.setAttribute('value','0')
                        if name == 'install':
                            if self.options.has_key('install') and self.options['install'] == '1':
                                step.setAttribute('value','1')
                            elif self.options.has_key('install_mini') and self.options['install_mini'] == '1':
                                step.setAttribute('value','1')
                            elif self.options.has_key('install_full') and self.options['install_full'] == '1':
                                step.setAttribute('value','1')
                            elif self.options.has_key('install_update') and self.options['install_update'] == '1':
                                step.setAttribute('value','1')
                            else:
                                step.setAttribute('value','0')
                                
            writer = open(bsFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
        
    def applyExtraOptions(self):
        #user-email and reasion info
        email = self.extraOptions['email']
        reason = self.extraOptions['reason']
        msg = '%s|%s' % (email,reason)
        msg = msg.replace('\\','/')
        msg = msg.replace('"',' ')
        msg = msg.replace('\'',' ')
        msg = msg.replace('\r',' ')
        msg = msg.replace('\n',' ')
        content = '{"msrc":"wk-user-info","content":"%s"}' % msg
        logging.info('send message from worker, sid:%s, message:%s' % (self.id,content))
        self.socket.send(content)
        #code base info
        svnFile = './buildswitch/svn.xml'
        try:
            dom = xml.dom.minidom.parse(svnFile)
            root = dom.documentElement
            cbName = ''
            cbVal = self.extraOptions['cbdetail']
            if self.extraOptions['codebase'] == '1':
                cbName = 'branch'
            elif self.extraOptions['codebase'] == '2':
                cbName = 'tag'
            elif self.extraOptions['codebase'] == '3':
                cbName = 'trunk'
                cbValue = 'HEAD'
            elif self.extraOptions['codebase'] == '4':
                cbName = 'revision'
            else:
                cbName = 'trunk'
            root.setAttribute('use',cbName)
            if self.options['locksvn'] == '1':
                root.setAttribute('lock','true')
            else:
                root.setAttribute('lock','false')
            if self.options['releasesvn'] == '1':
                root.setAttribute('unlock','true')
            else:
                root.setAttribute('unlock','false')
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                name = node.getAttribute('name')
                if name != cbName:
                    continue;
                else:
                    node.setAttribute('value',cbVal)
                    break
            writer = open(svnFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
        #markup code info
        svnFile = './buildswitch/MarkupCode.xml'
        try:
            dom = xml.dom.minidom.parse(svnFile)
            root = dom.documentElement
            mkName = ''
            mkVal = self.extraOptions['markupdetail']
            if self.extraOptions['markupcode'] == '0':
                mkName = 'none'
            elif self.extraOptions['markupcode'] == '1':
                mkName = '+branch'
            elif self.extraOptions['markupcode'] == '2':
                mkName = '+tag'
            elif self.extraOptions['markupcode'] == '3':
                mkName = '-branch'
            elif self.extraOptions['markupcode'] == '4':
                mkName = '-tag'
            else:
                mkName = 'none'
            root.setAttribute('use',mkName)
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                name = node.getAttribute('name')
                if name != mkName:
                    continue;
                else:
                    node.setAttribute('value',mkVal)
                    break
            writer = open(svnFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
        #misc info
        miscFile = './buildswitch/Misc.xml'
        try:
            dom = xml.dom.minidom.parse(miscFile)
            root = dom.documentElement
            for node in root.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                name = node.getAttribute('name')
                if self.options.has_key(name):
                    node.setAttribute('value',self.options[name])
                elif self.extraOptions.has_key(name):
                    node.setAttribute('value',self.extraOptions[name])
                else:
                    node.setAttribute('value','0')
            writer = open(miscFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)
        #package info
        pkgFile = './buildswitch/Package.xml'
        try:
            dom = xml.dom.minidom.parse(pkgFile)
            root = dom.documentElement
            if self.options.has_key('install'):
                root.setAttribute('install',self.options['install'])
            else:
                root.setAttribute('install','0')
            if self.options.has_key('install_mini'):
                root.setAttribute('install_mini',self.options['install_mini'])
            else:
                root.setAttribute('install_mini','0')
            if self.options.has_key('install_full'):
                root.setAttribute('install_full',self.options['install_full'])
            else:
                root.setAttribute('install_full','0')
            if self.options.has_key('install_update'):
                root.setAttribute('install_update',self.options['install_update'])
            else:
                root.setAttribute('install_update','0')
            writer = open(pkgFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            logging.error("error occers when parsing xml or run command:")
            logging.error(e)

        
    def applyBuildSettings(self):
        self.applySlnSettings()
        self.applyBuildOptions()
        self.applyExtraOptions()
        
    def run(self):
        nickname = ''
        if self.projName == 'bdkv':
            nickname = 'kvfastrelease'
        elif self.projName == 'bdm':
            nickname = 'mgrfastrelease'
        para = ('wk-build-log', self.id, self.socket)
        buildproject(nickname,para)
        
def InitBuildInfo(nickname,para):
    buildConfFile = './BuildSwitch/BuildStep.xml'
    buildStep = []
    try:
        dom = xml.dom.minidom.parse(buildConfFile)
        root = dom.documentElement
        for buildNode in root.childNodes:
            if buildNode.nodeType != buildNode.ELEMENT_NODE:
                continue
            if nickname.lower() != buildNode.getAttribute('nickname'):
                continue
            product = buildNode.getAttribute('product')
            buildstep.BuildStep.g_t_weight = 0
            buildstep.BuildStep.g_c_weight = 0
            
            for stepNode in buildNode.childNodes:
                if stepNode.nodeType != stepNode.ELEMENT_NODE:
                    continue
                name = stepNode.getAttribute('name')
                value = stepNode.getAttribute('value')
                order = stepNode.getAttribute('order')
                weight = stepNode.getAttribute('weight')
                buildstep.BuildStep.g_t_weight += int(weight)
                try:
                    clsName = ''
                    if product == 'bdm':
                        clsName = getattr(buildstep,buildstep.build_step_creator[name])
                    elif product == 'bdkv':
                        clsName = getattr(buildstep,buildstep.kvbuild_step_creator[name])
                    step = new.instance(clsName)
                    step.__init__(name,int(value),int(order),int(weight),para)
                    buildStep.append(step)
                except Exception,e:
                    logging.error("error occers when creating buildsteps")
                    logging.error(e)
                    return (buildStep,False)
        return (buildStep,True)
    except Exception,e:
        logging.error("error occers when initializing xbuild system")
        logging.error(e)
        return (buildStep,False)
    
def report(msrc, msg, para):
    if len(para) == 0:
        logging.info(msg)
    elif para[0] == 'wk-build-log':
        sid = para[1]
        ws = para[2]
        #整饰特殊字符
        msg = msg.replace('\\','/')
        msg = msg.replace('"',' ')
        msg = msg.replace('\'',' ')
        msg = msg.replace('\r',' ')
        msg = msg.replace('\n',' ')
        content = '{"msrc":"%s","content":"%s"}' % (msrc, msg)
        logging.info('send message from worker, sid:%s, message:%s' % (sid,content))
        ws.send(content)
        
def buildproject(nickname,para = ()):
    #initialize
    (buildStep,bInited) = InitBuildInfo(nickname,para)
    
    if not bInited:
        logging.info('configuration error, please check BuildSwitch/BuildStep.xml')
        return
    
    #reset progress
    report('wk-build-progress','0',para)
    #info print
    report('wk-build-log', 'XBuild Start', para)
    report('wk-build-log', '------------------------------------------------------', para)
    report('wk-build-log', 'Build Step(s)', para)
    report('wk-build-log', '------------------------------------------------------', para)
    
    #do homework
    buildStep.sort(lambda x,y: cmp(x.order,y.order))
    try:
        for item in buildStep:
            report('wk-build-log', '', para)
            report('wk-build-log', 'Step %d - %s' % (item.order,item), para)
            report('wk-build-log', '------------------------------------------------------', para)
            item.act()
    except Exception,e:
        logging.error(e)
        report('wk-status-change','error',para)
        return
    logging.info('build complete !!')
    report('wk-build-finish','',para)
    report('wk-status-change','idle',para)
            
def main(argc, argv):
    
    if argc != 2:
        print 'usage:python xbuild.py <nickname>'
        return
    
    #init logging system, it's told logging is threadsafe, so do NOT need to sync
    logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
    
    nickname = argv[1]
    buildproject(nickname)

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))


