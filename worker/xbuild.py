"""
@author    tomas
@date    2013-03-07
@desc
    express build mode,usage : python xbuild.py <nickname>
"""

import sys,os,conf,xml.dom.minidom,buildstep,new
import threading
import logging

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
        if settings[0] == 'X光':
            self.projName = 'bdkv'
        elif settings[0] == '极光':
            self.projName = 'bdm'
        self.slns = {}
        for item in settings[1].split(';'):
            slnName = item[0:item.find(',')]
            slnBuild = item[item.find(',')+1:]
            self.slns[slnName] = slnBuild
        self.options = {}
        for item in settings[2].split(';'):
            opName = item[0:item.find(',')]
            opVal = item[item.find(',')+1:]
            self.options[opName] = opVal
        self.extraOptions = {}
        iIndex = 0
        for i in range(3,6):
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
                    if product == self.projName:
                        node.setAttribute('build','1')
                    else:
                        node.setAttribute('build','0')
                    writer = open(confFile,'w')
                    dom.writexml(writer)
                    writer.close()
        except Exception,e:
            print "error occers when parsing xml or run command:"
            print e
        
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
                        name = step.getAttribute('name')
                        if self.options.has_key(name):
                            step.setAttribute('value',self.options[name])
                        elif name == 'prebuild' or name == 'postbuild':
                            step.setAttribute('value','1')
                        else:
                            step.setAttribute('value','0')
                writer = open(confFile,'w')
                dom.writexml(writer)
                writer.close()
        except Exception,e:
            print "error occers when parsing xml or run command:"
            print e
        
    def applyBuildSettings(self):
        self.applySlnSettings()
        self.applyBuildOptions()
        
def InitBuildInfo(nickname,para):
    buildConfFile = './BuildSwitch/BuildStep.xml'
    buildInfo = ('nickname','product','buildtype')
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
            buildtype = buildNode.getAttribute('type')
            buildInfo = (nickname,product,buildtype.split(','))
            buildstep.g_t_weight = 0
            buildstep.g_c_weight = 0
            
            for stepNode in buildNode.childNodes:
                if stepNode.nodeType != stepNode.ELEMENT_NODE:
                    continue
                name = stepNode.getAttribute('name')
                value = stepNode.getAttribute('value')
                order = stepNode.getAttribute('order')
                weight = stepNode.getAttribute('weight')
                buildstep.g_t_weight += weight
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
                    print "error occers when creating buildsteps"
                    print e
                    return (buildInfo,buildStep,False)
        return (buildInfo,buildStep,True)
    except Exception,e:
        print "error occers when initializing xbuild system"
        print e
        return (buildInfo,buildStep,False)
    
    def run(self):
        nickname = ''
        if self.projName == 'bdkv':
            nickname = 'bdkvfastrelease'
        elif self.projName == 'bdm':
            nickname = 'bdmfastrelease'
        para = ('wk-build-log', self.id, self.socket)
        buildproject(nickname,para)
        
def buildproject(nickname,para = ()):
    #initialize
    (buildInfo,buildStep,bInited) = InitBuildInfo(nickname,para)
    
    if not bInited:
        print 'configuration error, please check BuildSwitch/BuildStep.xml'
        return
    
    #info print
    print '\nXBuild Start\n-------------------------------'
    print 'Build Nickname: %s\nProduct: %s\nBuild Type: %s' % buildInfo
    print '\nBuild Step(s)\n-------------------------------'
    
    #do homework
    buildStep.sort(lambda x,y: cmp(x.order,y.order))
    for item in buildStep:
        print '\nStep %d - %s\n-------------------------------' % (item.order,item)
        item.act()
            
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


