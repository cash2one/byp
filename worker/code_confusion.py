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

confusion_folder = '..\\avclient_proj\\Source\\NetInstallHelpler\\'
sln_folder = '..\\avclient_proj\\Projects\\'
output_folder = '..\\basic\\Tools\\NSIS\\Plugins\\'

random_api = [
        'GetCurrentThreadId',
        'GetCurrentThread',
        'GetCurrentProcess',
        'GetLastError',
        'GetCommandLine',
        ]

def generate(nf, nDll, iStart):
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
        command = 'copy /Y ' + output_folder + 'KVNetInstallHelpler.dll .\\dll\\KVNetInstallHelper_%d.dll' % iCount
        os.system(command)
        command = 'copy /Y ' + output_folder + 'KVNetInstallHelpler.pdb .\\pdb\\KVNetInstallHelper_%d.pdb' % iCount
        os.system(command)

    #copy to archive
    command = 'copy /Y .\\dll\\*.dll \\\\10.52.174.35\\public\\aladdin\\DailyBuild\\kvnetinstallhelper\\'
    os.system(command)

def main(argc, argv):
    generate(16,300,1000)

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
