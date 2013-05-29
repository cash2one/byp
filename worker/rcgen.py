# coding=UTF-8
"""
@author    thomas
@date    2013-03-13
@desc
    auto generate BDMVersion.rc for each project

"""

import sys,os,conf,xml.dom.minidom

def main(argc, argv):
    if argc != 2:
        print 'usage:python rcgen.py <product_shortname (bdm|bdkv)>'
        return
    rcfile = ''
    if argv[1] == 'bdm':
        rcfile = conf.rclist_file
    elif argv[1] == 'bdkv':
        rcfile = conf.kv_rclist_file
    dom = xml.dom.minidom.parse(rcfile)
    root = dom.documentElement
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        projdir = node.getAttribute('projdir')
        modulename = node.getAttribute('modulename')
        filedesc = node.getAttribute('filedesc')
        command = conf.byp_bin_path + 'rcgen.exe --projdir="%s" --modulename="%s" --filedesc="%s"' % (projdir,modulename,filedesc)
        os.system(command.encode(sys.getfilesystemencoding()))

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
