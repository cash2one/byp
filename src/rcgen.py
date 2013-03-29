# encoding=utf-8
"""
@author    tomas
@date    2013-03-13
@desc
    auto generate BDMVersion.rc for each project

"""

import sys,os,conf,xml.dom.minidom

def main(argc, argv):
    dom = xml.dom.minidom.parse(conf.rclist_file)
    root = dom.documentElement
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        projdir = node.getAttribute('projdir')
        modulename = node.getAttribute('modulename')
        filedesc = node.getAttribute('filedesc')
        command = os.getcwd() + '\\AutoBuild\\rcgen.exe --projdir="%s" --modulename="%s" --filedesc="%s"' % (projdir,modulename,filedesc)
        os.system(command.encode(sys.getfilesystemencoding()))

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
