# coding=UTF-8
"""
@author thomas
@date   2013-10-30
@desc
    auto generate confusion.h and confusion.cpp
@change
    init ----------------------------------- 2013.10.30

"""

import os
import sys
import random
import sign

confusion_folder = '..\\..\\sharemem_rd\\avclient_proj\\Source\\NetInstallHelpler\\'
sln_folder = '..\\..\\sharemem_rd\\avclient_proj\\Projects\\'
plugin_folder = '..\\..\\sharemem_rd\\basic\\Tools\\NSIS\\Plugins\\'
output_folder = '..\\..\\sharemem_rd\\confusion\\'

random_api = [
        'GetCurrentThreadId',
        'GetCurrentThread',
        'GetCurrentProcess',
        'GetLastError',
        'GetCommandLine',
        ]

def generate(nf, nDll, iStart):
    #clean dll and pdb folder
    command = 'del /Q ' + output_folder + 'dll\\*.dll'
    os.system(command)
    command = 'del /Q ' + output_folder + 'pdb\\*.pdb'
    os.system(command)

    #update svn
    command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk ..\\basic\\tools'
    os.system(command)

    for iCount in range(iStart,nDll + iStart):
        #write confusion.h
        fp = open(confusion_folder + 'confusion.h', 'w')
        fp.writelines('#pragma once\n')
        for item in range(0,nf):
            fp.writelines('int CodeConfusion%d();\n' % item)
        fp.close()

        #write confusion.cpp
        fp = open(confusion_folder + 'confusion.cpp','w')
        fp.writelines('#include "stdafx.h"\n')
        fp.writelines('#include "confusion.h"\n')
        fp.writelines('#include <windows.h>\n')
        for item in range(0,nf):
            n_cir = random.randint(32,64)
            n_api = random.randint(0,4)
            n_sb = random.randint(8,128) / 4 * 4
            n_hb = random.randint(64,512) / 4 * 4
            r_char = random.randint(0,255)

            fp.writelines('int CodeConfusion%d(){\n' % item)
            fp.writelines('int s = 0;\n')
            fp.writelines('for(int i=0;i<%d;++i){\n' % n_cir)
            fp.writelines('s += i;}\n')
            fp.writelines('%s();\n' % random_api[n_api])
            fp.writelines('char szBuf[%d] = {0};\n' % n_sb)
            fp.writelines('memset(szBuf,%d,%d);\n' % (r_char,n_sb))
            fp.writelines('short *pBuf = new short[%d];\n' % n_hb)
            fp.writelines('memset(pBuf,%d,%d * 2);\n' % (r_char,n_hb))
            fp.writelines('delete [] pBuf;\n')
            fp.writelines('return s;}\n')
        fp.close()

        #vcbuild
        command = 'vcbuild.exe ' + sln_folder + 'KVNetInstallerHelper_RD.sln "KVRelease|Win32"'
        os.system(command)
        command = 'copy /Y ' + plugin_folder + 'KVNetInstallHelpler.dll ' + output_folder + 'dll\\KVNetInstallHelper_%d.dll' % iCount
        os.system(command)
        command = 'copy /Y ' + plugin_folder + 'KVNetInstallHelpler.pdb ' + output_folder + 'pdb\\KVNetInstallHelper_%d.pdb' % iCount
        os.system(command)

    #sign baidu
    sign.main(3, ['sign.py', 'bdkv', output_folder + 'dll\\'])
    
    #copy to archive
    command = 'copy /Y ' + output_folder + 'dll\\*.dll \\\\10.52.174.35\\public\\aladdin\\DailyBuild\\kvnetinstallhelper\\'
    os.system(command)

def main(argc, argv):
    if argc != 4:
        print 'usage : code_confusion.py <nFunc> <nDll> <nStart>'
    generate(int(argv[1]),int(argv[2]),int(argv[3]))

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
