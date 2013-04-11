"""
@author    tomas
@date    2013-03-07
@desc
    express build mode,usage : python xbuild.py <nickname>
"""

import sys,os,conf,xml.dom.minidom,buildstep,new
import threading

#worker thread
class Worker(threading.Thread):
    def __init__(self, ws, sid):
        self.socket = ws
        self.id = sid
        threading.Thread.__init__(self)
    
    def setInitParam(ctx):
        settings = ctx.split('|')
        self.projName = settings[0]
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
            self.extraOptions[settings[i][0:iReason]] = settings[i][iReason+1:]
        
        self.applyBuildSettings()
        
    def run(self):
        pass
        
    def applyBuildSettings(self):
        pass
        
def InitBuildInfo(nickname):
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
            
            for stepNode in buildNode.childNodes:
                if stepNode.nodeType != stepNode.ELEMENT_NODE:
                    continue
                name = stepNode.getAttribute('name')
                value = stepNode.getAttribute('value')
                order = stepNode.getAttribute('order')
                try:
                    clsName = ''
                    if product == 'bdm':
                        clsName = getattr(buildstep,buildstep.build_step_creator[name])
                    elif product == 'bdkv':
                        clsName = getattr(buildstep,buildstep.kvbuild_step_creator[name])
                    step = new.instance(clsName)
                    step.__init__(name,int(value),int(order))
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
    

def main(argc, argv):
    
    if argc != 2:
        print 'usage:python xbuild.py <nickname>'
        return
    
    nickname = argv[1]
    
    #initialize
    (buildInfo,buildStep,bInited) = InitBuildInfo(nickname)
    
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
    

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))


