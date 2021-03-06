﻿# coding=UTF-8
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
import fileop
import mmap
import struct
import string
import comm

confusion_folder = '..\\..\\aladdin_v1092\\avclient_proj\\Source\\OnlineWnd\\OnlineWnd\\'
dll_resource_folder = '..\\..\\aladdin_v1092\\avclient_proj\\Source\\OnlineWnd\\OnlineWnd\\dllResource\\'
sln_folder = '..\\..\\aladdin_v1092\\avclient_proj\\Projects\\'
plugin_folder = '..\\..\\aladdin_v1092\\basic\\Tools\\NSIS\\Plugins\\'
output_folder = '..\\..\\aladdin_v1092\\confusion\\'
svn_root_folder = '..\\..\\aladdin_v1092\\'

random_api = [
        'GetCurrentThreadId',
        'GetCurrentThread',
        'GetCurrentProcess',
        'GetLastError',
        'GetCommandLine',
        ]

def confusionDll(file, para):
    token = para[0]
    print file
    with open(file, "r+b") as f:
        mf = mmap.mmap(f.fileno(), 0)
        fs = mf.size()
        while fs > 0:
            b4 = struct.unpack("I", mf.read(4))[0]
            b4 = b4 ^ token
            mf.seek(-4, os.SEEK_CUR)
            mf.write(struct.pack("I", b4))
            fs = fs - 4
        mf.flush()
        mf.close()

def dllConfusion(token):
    command = 'del /Q ' + dll_resource_folder + '*.dll'
    os.system(command)
    command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk272 ' + svn_root_folder + 'avclient_proj'
    os.system(command)
    para = (int(token, 16), )
    fileop.FileOperationWithExtraPara(dll_resource_folder, confusionDll, para, ['*.dll'])

def generate(nf, nDll, iStart):
    #clean dll and pdb folder
    command = 'del /Q ' + output_folder + 'exe\\*.exe'
    os.system(command)
    command = 'del /Q ' + output_folder + 'pdb\\*.pdb'
    os.system(command)

    #remove confusion dll
    command = 'del /Q ' + dll_resource_folder + '*.dll'
    os.system(command)
    #update svn
    command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk272 ' + svn_root_folder + 'basic'
    os.system(command)
    command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk272 ' + svn_root_folder + 'avclient_proj'
    os.system(command)
    command = 'svn update --non-interactive --no-auth-cache --username buildbot --password bCRjzYKzk272 ' + svn_root_folder + 'stable_proj'
    os.system(command)

    for iCount in range(iStart,nDll + iStart):
        #write confusion.h
        fp = open(confusion_folder + 'confusion.h', 'w')
        xor_token = "0x%x%x%x%x%x%x%x%x" % (random.randint(0,15), random.randint(0,15), random.randint(0,15), random.randint(0,15), random.randint(0,15), random.randint(0,15), random.randint(0,15), random.randint(0,15))
        fp.writelines('#pragma once\n')
        fp.writelines('#define _CODE_CONFUSION 1\n')
        fp.writelines('#define _DLL_CONFUSION_KEY %s\n' % xor_token)
        for item in range(0,nf):
            n_cir = random.randint(32,64)
            n_api = random.randint(0,4)
            n_sb = random.randint(8,128) / 4 * 4
            n_hb = random.randint(64,512) / 4 * 4
            r_char = random.randint(0,255)

            fp.writelines('int CodeConfusion%d();\n' % item)

            fp.writelines('#define CallCodeConfusion%d \\\n' % item)
            fp.writelines('int _confusion_code_var_s = 0; \\\n')
            fp.writelines('for(int i=0;i<%d;++i){ \\\n' % n_cir)
            fp.writelines('_confusion_code_var_s += i;} \\\n')
            fp.writelines('_confusion_code_var_s += int(%s()); \\\n' % random_api[n_api])
            fp.writelines('char _confusion_code_var_szBuf[%d] = {0}; \\\n' % n_sb)
            fp.writelines('memset(_confusion_code_var_szBuf,%d,%d); \\\n' % (r_char,n_sb))
            fp.writelines('short *_confusion_code_var_spBuf = new short[%d]; \\\n' % n_hb)
            fp.writelines('memset(_confusion_code_var_spBuf,%d,%d * 2); \\\n' % (r_char,n_hb))
            fp.writelines('delete [] _confusion_code_var_spBuf;\n')
        fp.close()

        #40个里面随机取7个
        r_list = []
        while True:
            r_item = random.randint(0,65535) % 51 + 1
            if r_item not in r_list:
                r_list.append(r_item)
            if len(r_list) == 7:
                break

        print 'confusion selection list : '
        print r_list

        #confusion OnlineWnd.cpp
        file_r = open(confusion_folder + 'OnlineWnd.cpp')
        lines = file_r.readlines()
        file_r.close()
        for index in range(len(lines)):
            iStart = lines[index].find('CodeConfusion')
            if iStart == -1:
                continue
            else:
                iStart = iStart + 12
            iNum = 0
            if lines[index][iStart+1] == '(':
                iNum = int(lines[index][iStart+1:iStart+1])
            elif lines[index][iStart+2] == '(':
                iNum = int(lines[index][iStart+1:iStart+2])
            elif lines[index][iStart+3] == '(':
                iNum = int(lines[index][iStart+1:iStart+3])

            token = 'CodeConfusion%d' % iNum
            rtoken = 'CodeConfusion%d' % random.randint(0,255)
            if lines[index].find('CodeConfusion') != -1:
                    lines[index] = lines[index].replace(token,rtoken)
        file_w = open(confusion_folder + 'OnlineWnd1.cpp', "w")
        file_w .writelines(lines)
        file_w .close()

        #write confusion.cpp
        fp = open(confusion_folder + 'confusion.cpp','w')
        fp.writelines('#include "stdafx.h"\n')
        fp.writelines('#include "confusion.h"\n')
        fp.writelines('#include <windows.h>\n')
        for item in range(0,nf):
            n_cir = random.randint(32,256)
            m_lp1 = random.randint(0,4)
            m_lp2 = random.randint(0,8)
            m_lp3 = random.randint(0,16)
            m_lp4 = random.randint(0,32)
            m_lp5 = random.randint(0,64)

            fp.writelines('int CodeConfusion%d(){\n' % item)
            fp.writelines('int _confusion_sum = 0;')

            #后面从这7个里面随机
            for item in range(0,m_lp1):
                confusion_file = '.\\code_confusion\\%d.cpp' % r_list[(random.randint(0,65535) % 7)]
                fp.writelines(comm.getMsg(confusion_file).replace('$a',str(random.randint(0,64))))
            for item in range(0,m_lp2):
                confusion_file = '.\\code_confusion\\%d.cpp' % r_list[(random.randint(0,65535) % 7)]
                fp.writelines(comm.getMsg(confusion_file).replace('$a',str(random.randint(0,32))))
            for item in range(0,m_lp3):
                confusion_file = '.\\code_confusion\\%d.cpp' % r_list[(random.randint(0,65535) % 7)]
                fp.writelines(comm.getMsg(confusion_file).replace('$a',str(random.randint(0,16))))
            for item in range(0,m_lp4):
                confusion_file = '.\\code_confusion\\%d.cpp' % r_list[(random.randint(0,65535) % 7)]
                fp.writelines(comm.getMsg(confusion_file).replace('$a',str(random.randint(0,8))))
            for item in range(0,m_lp5):
                confusion_file = '.\\code_confusion\\%d.cpp' % r_list[(random.randint(0,65535) % 7)]
                fp.writelines(comm.getMsg(confusion_file).replace('$a',str(random.randint(0,4))))

            fp.writelines('return _confusion_sum;}\n')
        fp.close()
        
        #dll confusion
        dllConfusion(xor_token)

        #generte random data to cu.dll, 3M random data
        fp = open(confusion_folder + 'dllResource\\cu.dll','w')
        for i in range(1, random.randint(0, 6144)):
            for j in range(0,15):
                fp.write(''.join(random.sample(string.ascii_letters + string.digits, 32)))
        fp.close()

        #vcbuild
        command = 'vcbuild.exe /rebuild ' + sln_folder + 'AladdinBind.sln "KVRelease|Win32"'
        os.system(command)
        command = 'copy /Y ' + plugin_folder + 'bind.exe ' + output_folder + 'exe\\bind%d.exe' % iCount
        os.system(command)
        command = 'copy /Y ' + plugin_folder + 'bind.pdb ' + output_folder + 'pdb\\bind%d.pdb' % iCount
        os.system(command)
        
        #pack upx shell
        command = '..\\bin\\upx.exe -1 -v ' + output_folder + 'exe\\bind%d.exe' % iCount
        os.system(command)

    #sign baidu
    sign.main(3, ['sign.py', 'bdkv', output_folder + 'exe\\'])
    
    #copy to archive
    command = 'copy /Y ' + output_folder + 'exe\\*.exe \\\\10.52.174.35\\public\\aladdin\\DailyBuild\\aladdin_bind_v1092\\'
    os.system(command)

def main(argc, argv):
    if argc != 4:
        print 'usage : code_confusion.py <nFunc> <nDll> <nStart>'
    generate(int(argv[1]),int(argv[2]),int(argv[3]))

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))
