"""
@author    tomas
@date    2013-01-21
@desc
    build solutions optional,configurations are in .\BuildSwitch\SOLUTION_NAME.xml
    build="1"------------------------build this solution
    build="0" or any other else------DO NOT build this solution
"""

import sys,os,conf,xml.dom.minidom

def main(argc, argv):
    if argc != 2 and argc != 3 and argc != 4:
        print 'usage:python partial_build.py <product_shortname (bdm|bdkv)> <build_type [optional](express[default]|full)> <force [optional]>'
        return
    
    checklogFile = ''
    errDir = ''
    product = argv[1].lower()
    if product == 'bdm':
        checklogFile = conf.checklog_file
        errDir = 'err\\'
    elif product == 'bdkv':
        checklogFile = conf.kvchecklog_file
        errDir = 'kverr\\'
    if not checklogFile:
        print 'configuration error,please check conf.py'
        return
    
    build_type = 'express'
    svnAction = 'update'
    vcbuildAction = '/build'
    if argc == 3 and argv[2].lower() == 'full':
        build_type = 'full'
        svnAction = 'checkout'
        vcbuildAction = '/rebuild'
    
    bForce = False
    if argc == 4 and argv[3].lower() == 'force':
        bForce = True
    
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
        
    for item in slns:
        confFile = './BuildSwitch/'+item+'.xml'
        bChecked = False
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
                type = node.getAttribute('type')
                logName = ''
                if type.lower().find('debug') != -1:
                    logName = 'Debug'
                elif type.lower().find('release') != -1:
                    logName = 'Release'
                else:
                    logName = type[0:type.find('|')]
                node.setAttribute('build','0')
                if not bChecked:
                    if svnAction == 'checkout':
                        command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD http://192.168.10.242:8000/client/"  + svnDir + " ..\\..\\" + dir
                    elif svnAction == 'update':
                        command = "svn " + svnAction + " --non-interactive --no-auth-cache --username buildbot --password 123456 --revision HEAD ..\\..\\" + dir
                    print command
                    os.system(command)
                    bChecked = True
                command = "vcbuild " + vcbuildAction + " /time /M16 /errfile:AutoBuild\\" + errDir + item + logName + ".log ..\\..\\" \
                 + dir + "\\Projects\\" + item + ".sln \"" + type + "\""
                print command
                os.system(command)
            writer = open(confFile,'w')
            dom.writexml(writer)
            writer.close()
        except Exception,e:
            print "error occers when parsing xml or run command:"
            print e
    

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
