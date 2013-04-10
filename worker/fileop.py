"""
@author    tomas
@date    2013-02-20
@desc
    Do file operation in dir recursively
@change
    add local sign support ------------------------------ 2013.02.20
    add baidu offical sign support ---------------------- 2013.02.22
    add show_specific_file support ---------------------- 2013.02.22
    add kav sign support -------------------------------- 2013.02.26
    add file exist verify support ----------------------- 2013.03.06
    add file version and sign verify support ------------ 2013.03.06
    add rcgen support ----------------------------------- 2013.03.13
"""

import sys,os,glob,httplib,urllib,mimetypes,comm,conf,xml.dom.minidom,win32api,shutil


def FileOperation(dir,op,fileType,excluded_dir=[]):
    #root dir
    for type in fileType:
        destPath = dir + type
        for file in glob.glob(destPath): 
            excluded = False
            for exdir in excluded_dir:
                if file.lower().find(exdir) != -1:
                    excluded = True
                    break
            if not excluded:
                op(file)
    for root, folders,files in os.walk(dir): 
        for type in fileType:    
            for folder in folders:
                if root[-1] == '\\':
                    destPath = root + folder + '\\' + type
                else:
                    destPath = root + '\\' + folder + '\\' + type
                for file in glob.glob(destPath): 
                    excluded = False
                    for exdir in excluded_dir:
                        if file.lower().find(exdir) != -1:
                            excluded = True
                            break
                    if not excluded:
                        op(file)


def FileOperationWithExtraPara(dir,op,para,fileType,excluded_dir=[]):
    #root dir
    for type in fileType:
        destPath = dir + type
        for file in glob.glob(destPath):
            excluded = False
            for exdir in excluded_dir:
                if file.lower().find(exdir) != -1:
                    excluded = True
                    break
            if not excluded:
                op(file,para)
    for root, folders,files in os.walk(dir):
        for type in fileType:    
            for folder in folders:
                if root[-1] == '\\':
                    destPath = root + folder + '\\' + type
                else:
                    destPath = root + '\\' + folder + '\\' + type
                for file in glob.glob(destPath): 
                    excluded = False
                    for exdir in excluded_dir:
                        if file.lower().find(exdir) != -1:
                            excluded = True
                            break
                    if not excluded:
                        op(file,para)


def Show(file):
    print file


def Sign(file):
    print 'Signning File: ' + file
    command = os.getcwd() + '\\AutoBuild\\FileSign.exe /s ' + file
    os.system(command)
    

def SignKav(file):
    print 'Signning File With Kav: ' + file
    command = os.getcwd() + '\\AutoBuild\\KavSign.exe /s"' + file + '" /u"keys\\PrivateKey.sgn"'
    os.system(command)

def GenRC(file,writer):
    lfile = file.lower()
    if lfile.find('\\basic\\') != -1 or lfile.find('\\vdc_proj\\') != -1 or lfile.find('\\webshield_proj\\') != -1:
        print 'ignoring file : %s' % file
    else:
        print 'analysing file : %s' % file
        index = file.rfind('\\')
        projdir = file[6:index]
        modulename = file[index+1:file.rfind('.vcproj')]
        item = '<item projdir="%s" modulename="%s.dll" filedesc="%s"/>\n' % (projdir,modulename,'')
        writer.write(item)
        
def GenRCFile(path,op,ftype):
    writer = open(conf.rclist_file,'w')
    writer.write('<?xml version="1.0" ?><conf>\n')
    FileOperationWithExtraPara(path,op,writer,ftype)
    writer.write('</conf>')
    writer.close()

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def encode_multipart_formdata(fields, files, blanks):
    BOUNDARY = '----------boundary_post_file_to_sign_by_tomas_sw_kh'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename[filename.rfind('\\')+1:]))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    for name in blanks:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename=""' % name)
        L.append('Content-Type: application/octet-stream')
        L.append('')
        L.append('')
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def post_multipart(host, selector, fields, files, blanks):
    content_type, body = encode_multipart_formdata(fields, files, blanks)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()


def SignBaidu(file,para):
    product = para[0]
    signType = para[1]
    sign_product = ''
    if product == 'bdm':
        sign_product = conf.sign_file_product.encode(sys.getfilesystemencoding())
    elif product == 'bdkv':
        sign_product = conf.kvsign_file_product.encode(sys.getfilesystemencoding())
    file_path = file[0:file.rfind('\\')+1]
    file_name = file[file.rfind('\\')+1:]
    print 'Signning File ' + file + ' through vpn connection to ' + conf.cerf_addr
    files,fields = [],[]
    fields.append(('desc',sign_product))
    fields.append(('cert',signType))
    files.append(('f1',file,comm.getFileBuf(file)))
    #blanks = ['f2','f3','f4','f5','f6','f7','f8','f9']
    blanks = []
    
    digitalSign = ''
    if signType == '1':
        digitalSign = 'baidu_cn'
    elif signType == '2':
        digitalSign = 'baidu_bj_netcom'
    elif signType == '3':
        digitalSign = 'baidu_jp'
    
    for i in range(0,5):
        response = post_multipart(conf.cerf_addr,'/sign.php',fields,files,blanks)
        print response
        urllib.urlretrieve('http://' + conf.cerf_addr + '/OutPut/' + file_name, file + '.sign')
        
        command = os.getcwd() + '\\AutoBuild\\SignVerify.exe ' + file + '.sign ' + digitalSign
        ret = os.system(command)
        if ret == 0:
            shutil.move(file+'.sign', file)
            break;
        
        if i == 4:
            print '\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a'
            raise 'Sign baidu official digital signature failed.'
        
    return

def SignBaiduOfficial(path,ftype,product,excluded_dir):
    done = False
    signId = '0'
    signConfFile = ''
    logFile = ''
    if product == 'bdm':
        signConfFile = conf.sign_conf_file
        logFile = conf.verify_log_file
    elif product == 'bdkv':
        signConfFile = conf.kvsign_conf_file
        logFile = conf.kvverify_log_file
    dom = xml.dom.minidom.parse(signConfFile)
    root = dom.documentElement
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        if node.getAttribute('sign') != '1':
            continue
        if node.getAttribute('sign') == '1':
            if done:
                #node.setAttribute('sign','0')
                continue
            type = node.getAttribute('type')
            if type == 'baidu_cn':
                signId = '1'
            elif type == 'baidu_bj_netcom':
                signId = '2'
            elif type == 'baidu_jp':
                signId = '3'
            #node.setAttribute('sign','0')
            done = True
    writer = open(signConfFile,'w')
    dom.writexml(writer)
    writer.close()
    
    if done:
        FileOperationWithExtraPara(path,SignBaidu,(product,signId),ftype,excluded_dir)

def FileVerify(file,para):
    root = para[0]
    writer = para[1]
    rootdir = para[2].lower()
    file = file.lower()
    file = file[file.find(rootdir) + len(rootdir):]
    check = 'NOT IN THE CHECKLIST'
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        path = node.getAttribute('path')
        if file.lower() == path.lower():
            node.setAttribute('check','1')
            check = 'FOUND'
            break
    
    log = 'Verifing file: %s --- %s\n' % (file,check)
    writer.write(log)


def CheckFileUnexist(root,writer):
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        if '1' != node.getAttribute('check'):
            log = 'Verifing file: %s --- NOT FOUND\n' % node.getAttribute('path')
            writer.write(log)


def VerifyFileExist(path,ftype,product,logfile = '',configfile = ''):
    confFile = ''
    logFile = ''
    if product == 'bdm':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.verify_log_file
        if configfile != '':
            confFile = configfile
        else:
            confFile = conf.exist_verify_file
    elif product == 'bdkv':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.kvverify_log_file
        if configfile != '':
            confFile = configfile
        else:
            confFile = conf.kvexist_verify_file
    
    dom = xml.dom.minidom.parse(confFile)
    root = dom.documentElement
    writer = open(logFile,'a')
    writer.write('\n----------------Verify Files----------------\n')
    FileOperationWithExtraPara(path,FileVerify,(root,writer,path[path[:-1].rfind('\\')+1:]),ftype)
    CheckFileUnexist(root,writer)
    writer.close()

def VersionVerify(file,para):
    verInfo = para[0]
    writer = para[1]
    company = verInfo[0]
    trademark = verInfo[1]
    copyright = verInfo[2]
    productname = verInfo[3]
    productversion = verInfo[4]

    log = '\nverifing file version : %s\n' % file
    writer.write(log)
    try:  
        propNames = ('Comments', 'InternalName', 'ProductName',  
            'CompanyName', 'LegalCopyright', 'ProductVersion',  
            'FileDescription', 'LegalTrademarks', 'PrivateBuild',  
            'FileVersion', 'OriginalFilename', 'SpecialBuild')  
      
        props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}
        
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc  
        fixedInfo = win32api.GetFileVersionInfo(file, '\\')  
        props['FixedFileInfo'] = fixedInfo  
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,  
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,  
                fixedInfo['FileVersionLS'] % 65536)  
  
        # \VarFileInfo\Translation returns list of available (language, codepage)  
        # pairs that can be used to retreive string info. We are using only the first pair.  
        lang, codepage = win32api.GetFileVersionInfo(file, '\\VarFileInfo\\Translation')[0]  
  
        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle  
        # two are language/codepage pair returned from above  
  
        strInfo = {}  
        for propName in propNames:  
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)  
            ## print str_info  
            strInfo[propName] = win32api.GetFileVersionInfo(file, strInfoPath)  
  
        props['StringFileInfo'] = strInfo  

        #company 
        if company == props['StringFileInfo']['CompanyName']:
            writer.write('company verified\n')
        else:
            log = 'company DOES NOT match, is : %s\n' % props['StringFileInfo']['CompanyName']
            writer.write(log)
        #trademark
        if trademark == props['StringFileInfo']['LegalTrademarks']:
            writer.write('trademark verified\n')
        else:
            log = 'trademark DOES NOT match, is : %s\n' % props['StringFileInfo']['LegalTrademarks']
            writer.write(log)
        #copyright
        if copyright == props['StringFileInfo']['LegalCopyright']:
            writer.write('copyright verified\n')
        else:
            log = 'copyright DOES NOT match, is : %s\n' % props['StringFileInfo']['LegalCopyright']
            writer.write(log)
        #productname
        if productname == props['StringFileInfo']['ProductName']:
            writer.write('productname verified\n')
        else:
            log = 'productname DOES NOT match, is : %s\n' % props['StringFileInfo']['ProductName']
            writer.write(log)
        #productversion
        if productversion == props['FileVersion']:
            writer.write('productversion verified\n')
        else:
            log = 'productversion DOES NOT match, is : %s\n' % props['FileVersion']
            writer.write(log)

    except Exception,e:
        log = 'error while verify file version : %s' % file
        writer.write(log)
        writer.write(str(e))



def GetProductVersion(product):
    company = conf.ver_company_name
    trademark = conf.ver_legal_trademarks
    copyright = conf.ver_copyright
    productname = ''
    buildlinefile = ''
    bn1 = '1'
    bn2 = '0'
    bn3 = ''
    bn4 = ''
    productversion = ''
    if product == 'bdm':
        productname = conf.ver_product_manager
        buildlinefile = './SetupScript/include/buildline.nsi'
    elif product == 'bdkv':
        productname = conf.ver_product_antivirus
        buildlinefile = './KVSetupScript/include/buildline.nsi'
    ctx = comm.getMsg(buildlinefile)
    index = ctx.find('"')+1
    bn3 = ctx[index:index+1]
    if bn3 == '0' and product == 'bdm':
        bn4 = comm.getMsg(conf.customBuildIdFile)
    elif bn3 == '0' and product == 'bdkv':
        bn4 = comm.getMsg(conf.kvCustomBuildIdFile)
    elif bn3 == '1' and product == 'bdm':
        bn4 = comm.getMsg(conf.versionBuildIdFile)
    elif bn3 == '1' and product == 'bdkv':
        bn4 = comm.getMsg(conf.kvVersionBuildIdFile)
    productversion = '%s.%s.%s.%s' % (bn1,bn2,bn3,bn4)
    return (company,trademark,copyright,productname,productversion)

def VerifyFileVersion(path,ftype,product,logfile = ''):
    logFile = ''
    if product == 'bdm':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.verify_log_file
    elif product == 'bdkv':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.kvverify_log_file
    verInfo = GetProductVersion(product)
    writer = open(logFile,'a')
    writer.write('\n----------------Verify File Version----------------\n')
    FileOperationWithExtraPara(path,VersionVerify,(verInfo,writer),ftype)
    writer.close()


def DriverSignVerify(file,writer):
    log = ''
    command = os.getcwd() + '\\AutoBuild\\FileSign.exe /v ' + file
    ret = os.system(command)
    if ret == 0:
        log = 'Verifing driver sign: %s --- SIGNED\n' % file
    else:
        log = 'Verifing driver sign: %s --- NOT SIGNED\n' % file
    writer.write(log)


def VerifyDriverSign(path,ftype,product,logfile = ''):
    logFile = ''
    if product == 'bdm':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.verify_log_file
    elif product == 'bdkv':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.kvverify_log_file
    writer = open(logFile,'a')
    writer.write('\n----------------Verify Driver Sign----------------\n')
    FileOperationWithExtraPara(path,DriverSignVerify,writer,ftype)
    writer.close()



def KavSignVerify(file,writer):
    log = ''
    command = os.getcwd() + '\\AutoBuild\\ChkKavSign.exe ' + file
    ret = os.system(command)
    if ret == 0:
        log = 'Verifing kav sign: %s --- SIGNED\n' % file
    else:
        log = 'Verifing kav sign: %s --- NOT SIGNED\n' % file
    writer.write(log)
    

def VerifyKavSign(path,ftype,product,logfile = ''):
    logFile = ''
    if product == 'bdm':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.verify_log_file
    elif product == 'bdkv':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.kvverify_log_file
    writer = open(logFile,'a')
    writer.write('\n----------------Verify Kav Sign----------------\n')
    FileOperationWithExtraPara(path,KavSignVerify,writer,ftype)
    writer.close()



def BaiduVerify(file,para):
    digitalSign = para[0]
    writer = para[1]
    command = os.getcwd() + '\\AutoBuild\\SignVerify.exe ' + file + ' ' + digitalSign
    ret = os.system(command)
    if ret == 0:
        log = 'Verifing baidu sign: %s --- SIGNED\n' % file
    else:
        log = 'Verifing baidu sign: %s --- NOT SIGNED\n' % file
    writer.write(log)


def VerifyBaiduSign(path,ftype,product,logfile = '',configfile = ''):
    done = False
    digitalSign = ''
    signConfFile = ''
    logFile = ''
    if product == 'bdm':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.verify_log_file
        if configfile != '':
            signConfFile = configfile
        else:
            signConfFile = conf.sign_conf_file
    elif product == 'bdkv':
        if logfile != '':
            logFile = logfile
        else:
            logFile = conf.kvverify_log_file
        if configfile != '':
            signConfFile = configfile
        else:
            signConfFile = conf.kvsign_conf_file
    dom = xml.dom.minidom.parse(signConfFile)
    root = dom.documentElement
    for node in root.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        if node.getAttribute('verify') != '1':
            continue
        if node.getAttribute('verify') == '1':
            if done:
                #node.setAttribute('verify','0')
                continue
            digitalSign = node.getAttribute('type')
            #node.setAttribute('verify','0')
            done = True
    writer = open(signConfFile,'w')
    dom.writexml(writer)
    writer.close()
    
    if done:
        writer = open(logFile,'a')
        writer.write('\n----------------Verify Baidu Sign----------------\n')
        FileOperationWithExtraPara(path,BaiduVerify,(digitalSign,writer),ftype)
        writer.close()

def GenFileList(file,para):
    writer = para[0]
    rootdir = para[1].lower()
    file = file.lower()
    file = file[file.find(rootdir) + len(rootdir):]
    line = '<file path="%s"/>\n' % file
    writer.write(line)


def GenFileVerify(path,ftype,product,conffile = ''):
    confFile = ''
    if product == 'bdm':
        if conffile != '':
            confFile = conffile
        else:
            confFile = conf.exist_verify_file
    elif product == 'bdkv':
        if conffile != '':
            confFile = conffile
        else:
            confFile = conf.kvexist_verify_file
    writer = open(confFile,'w')
    writer.write('<?xml version="1.0" ?><conf>\n')
    FileOperationWithExtraPara(path,GenFileList,(writer,path[path[:-1].rfind('\\')+1:]),ftype)
    writer.write('</conf>')
    writer.close()
    

def main(argc, argv):
    if argc < 3:
        print '''
usage:
python fileop.py <command> <dir> [filetype] [extra_para (command dependent)]
supported command(s): 
--------------------------------------------------------------------------
show                                  - show files
kvsign                                - kvdriver sign files
kvsign_kav                            - kav sign files
sign_baidu                            - sign manager baidu official
kvsign_baidu                          - sign kv baidu official
verify_file_exist                     - verify manager files
kvverify_file_exist                   - verify kv files
verify_file_version                   - verify manager file versions
kvverify_file_version                 - verify kv file versions
kvverify_driver_sign                  - verify kv driver sign
kvverify_kav_sign                     - verify kv kav sign
verify_baidu                          - verify manager baidu official
kvverify_baidu                        - verify kv baidu official
gen_file_list                         - generate manager verify file list
kvgen_file_list                       - generate kv verify file list
gen_rc_list                           - generate rc list
               '''
        return

    argv[2] = argv[2].strip('"')
    if argv[2][-1] != '\\':
        argv[2] += '\\'
    
    ftype = []
    if argc == 3:
        ftype.append('*.*')
    else:
        ftype = argv[3].split(',')
        
    extra_para1 = ''
    if argc >= 5:
        extra_para1 = argv[4]
    
    extra_para2 = ''
    if argc >= 6:
        extra_para2 = argv[5]
    
    if argv[1] == 'show':
        FileOperation(argv[2],Show,ftype)
    elif argv[1] == 'kvsign':
        FileOperation(argv[2],Sign,ftype)
    elif argv[1] == 'kvsign_kav':
        FileOperation(argv[2],SignKav,ftype)
    elif argv[1] == 'sign_baidu':
        SignBaiduOfficial(argv[2],ftype,'bdm')
    elif argv[1] == 'kvsign_baidu':
        SignBaiduOfficial(argv[2],ftype,'bdkv',conf.kv_official_sign_excluded_dir)
    elif argv[1] == 'verify_file_exist':
        VerifyFileExist(argv[2],ftype,'bdm',extra_para1,extra_para2)
    elif argv[1] == 'kvverify_file_exist':
        VerifyFileExist(argv[2],ftype,'bdkv',extra_para1,extra_para2)
    elif argv[1] == 'verify_file_version':
        VerifyFileVersion(argv[2],ftype,'bdm',extra_para1)
    elif argv[1] == 'kvverify_file_version':
        VerifyFileVersion(argv[2],ftype,'bdkv',extra_para1)
    elif argv[1] == 'kvverify_driver_sign':
        VerifyDriverSign(argv[2],ftype,'bdkv',extra_para1)
    elif argv[1] == 'kvverify_kav_sign':
        VerifyKavSign(argv[2],ftype,'bdkv',extra_para1)
    elif argv[1] == 'verify_baidu_sign':
        VerifyBaiduSign(argv[2],ftype,'bdm',extra_para1,extra_para2)
    elif argv[1] == 'kvverify_baidu_sign':
        VerifyBaiduSign(argv[2],ftype,'bdkv',extra_para1,extra_para2)
    elif argv[1] == 'gen_file_list':
        GenFileVerify(argv[2],ftype,'bdm',extra_para1)
    elif argv[1] == 'kvgen_file_list':
        GenFileVerify(argv[2],ftype,'bdkv',extra_para1)
    elif argv[1] == 'gen_rc_list':
        GenRCFile(argv[2],GenRC,ftype)

if "__main__" == __name__:
    sys.exit(main(len(sys.argv),sys.argv))