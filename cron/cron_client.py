# coding=UTF-8
import os,sys,logging,time,websocketclt,socket

cron_tasks = {
    'mgr_full_without_tag' : "{\"msrc\":\"ws-btn-build\",\"content\":\"93954138-b02b-46cf-bd19-a9b3a2d67c79|卫士|commonlib,0;skin,0;logicmisc,1;logicutils,1;client,1;commondll,1;syscleanerlib,1;luaVM,1;syscleaner,1;soacceleratorlib,1;soacceleratorplugin,1;swmanager,1;main,1;trojanscan,1;antivirusGJ,0;drivermanager,0;avhips,0;patcher,1;bd0001,0;attack,0;bdkitUtils,0|locksvn,0;rewriteversion,1;rcgen,1;svn,3;prebuild,2;install_mini,0;sign,1;install_silence,0;build,1;buildtype,3;ignorefault,1;install_update,0;rebase,1;install,1;pack,1;verify,0;send,1;releasesvn,0;symadd,1;xmarkup,1;sendmail,1;verifyinstaller,0;signinstaller,1;installermd5,0;commit,1|markupcode,0|markupdetail,bdm_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,2|v3,0|v4,$auto|postfix,$postfix|archive,$share/public/dailybuild/$version|reason,BaiduAn DB|email,sw_xt@baidu.com|supplyid,m50001,n50000|codebase,3|cbdetail,HEAD\"}",
             
    'bdkv_release_without_tag' : "{\"msrc\":\"ws-btn-build\",\"content\":\"9f638264-5ae4-47b5-bb21-934a3c97992f|杀毒|commonlib,0;skin,0;logicmisc,1;logicutils,1;client,1;commondll,1;avcommon,1;filemon,1;avhips,1;drivermanager,1;sysrepair,1;antivirus,1;bdkv,1;bd0001,1;defense,1;attack,1;repair,1;bdkitUtils,1|locksvn,0;rewriteversion,1;rcgen,1;svn,3;prebuild,2;install_mini,0;sign,1;install_silence,0;build,1;buildtype,2;ignorefault,1;rebase,1;install,1;install_update,0;install_full,0;pack,1;verify,0;send,1;releasesvn,0;symadd,1;xmarkup,0;sendmail,1;verifyinstaller,0;signinstaller,1;commit,1;installermd5,0|markupcode,0|markupdetail,bdkv_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,5|v3,0|v4,$auto|postfix,$postfix|archive,$share/public/kvdailybuild/1.main/$version|reason,BaiduSd DB|email,sw_aq@baidu.com|supplyid,m10001,n10000,f10015|codebase,1|cbdetail,1.0beta3_dev\"}",
             
    'daily_kvadapt' : "{\"msrc\":\"ws-btn-build\",\"content\":\"2cd6469e-bf13-4124-91a0-103e949c7abc|杀毒|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;avcommon,0;filemon,0;avhips,0;drivermanager,0;sysrepair,0;antivirus,0;bdkv,0;bd0001,0;defense,0;attack,0;repair,0;bdkitUtils,0;websafe,0;ave,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;install_full,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdkv_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,3|v3,0|v4,1055|postfix,$postfix|archive,$share/public/OnlineSetup/$date_kvadapt_50|reason,Supplyid448|email,zhangmin@baidu.com|supplyid,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111,m11111|codebase,1|cbdetail,1.0beta3_dev\"}",

    'daily_bdmadapt' : "{\"msrc\":\"ws-btn-build\",\"content\":\"437e7118-5abc-4e6e-896f-6dcaad475a48|卫士|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;syscleanerlib,0;luaVM,0;syscleaner,0;pluginmanager,0;sysfixer,0;soacceleratorlib,0;soacceleratorplugin,0;swmanager,0;main,0;trojanscan,0;antivirusGJ,0;drivermanager,0;avhips,0;bd0001,0;patcher,0;attack,0;bdkitUtils,0;android_basic,0;android,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdm_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,1|v3,0|v4,489|postfix,$postfix|archive,$share/public/OnlineSetup_GJ/$date_bdmadapt_50|reason,BaiduAn SupplyI|email,sw_xt@baidu.com|supplyid,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555,m55555|codebase,3|cbdetail,HEAD\"}",

    'daily_combine' : "{\"msrc\":\"ws-btn-build\",\"content\":\"9f648767-08d0-4548-8fc2-fe09279b16d0|杀毒|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;avcommon,0;filemon,0;avhips,0;drivermanager,0;sysrepair,0;antivirus,0;bdkv,0;bd0001,0;defense,0;attack,0;repair,0;bdkitUtils,0;websafe,0;ave,0|locksvn,0;rewriteversion,1;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,0;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,1;rebase,0;install,1;install_update,0;install_full,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdkv_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,2|v3,0|v4,$auto|postfix,$postfix|archive,$share/public/OnlineSetup/$date_2in1_50|reason,BaiduSd DB|email,sw_aq@baidu.com|supplyid,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001,m10001|codebase,1|cbdetail,1.0beta3_dev\"}",

    'daily_combine_bdkv' : "{\"msrc\":\"ws-btn-build\",\"content\":\"b981fc4c-da75-44ee-8d2a-3a54a4c88c3a|杀毒|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;avcommon,0;filemon,0;avhips,0;drivermanager,0;sysrepair,0;antivirus,0;bdkv,0;bd0001,0;defense,0;attack,0;repair,0;bdkitUtils,0;websafe,0;ave,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;install_full,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdkv_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,3|v3,0|v4,1055|postfix,$postfix|archive,$share/public/OnlineSetup/$date_combine_bdkv_50|reason,Supplyid448|email,zhangmin@baidu.com|supplyid,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001,m600001|codebase,1|cbdetail,1.0beta3_dev\"}",

    'daily_combine_bdm' : "{\"msrc\":\"ws-btn-build\",\"content\":\"9f648767-08d0-4548-8fc2-fe09279b16d0|卫士|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;syscleanerlib,0;luaVM,0;syscleaner,0;pluginmanager,0;sysfixer,0;soacceleratorlib,0;soacceleratorplugin,0;swmanager,0;main,0;trojanscan,0;antivirusGJ,0;drivermanager,0;avhips,0;bd0001,0;patcher,0;attack,0;bdkitUtils,0;android_basic,0;android,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdm_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,1|v3,0|v4,489|postfix,$postfix|archive,$share/public/OnlineSetup_GJ/$date_combine_bdm_50|reason,BaiduAn SupplyI|email,sw_xt@baidu.com|supplyid,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038,m200038|codebase,3|cbdetail,HEAD\"}",

    'daily_bdkv' : "{\"msrc\":\"ws-btn-build\",\"content\":\"3c2f48cc-40fa-4d77-a26d-12345c3ab1d2|杀毒|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;avcommon,0;filemon,0;avhips,0;drivermanager,0;sysrepair,0;antivirus,0;bdkv,0;bd0001,0;defense,0;attack,0;repair,0;bdkitUtils,0;websafe,0;ave,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;install_full,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdkv_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,5|v3,0|v4,1092|postfix,$postfix|archive,$share/public/OnlineSetup/$date_bdkv_50|reason,Supplyid448|email,zhangmin@baidu.com|supplyid,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000,n10000|codebase,1|cbdetail,1.0beta3_dev\"}",

    'daily_bdm' : "{\"msrc\":\"ws-btn-build\",\"content\":\"7bf00dca-5fe9-479b-a676-1dc6d260d61a|卫士|commonlib,0;skin,0;logicmisc,0;logicutils,0;client,0;commondll,0;syscleanerlib,0;luaVM,0;syscleaner,0;pluginmanager,0;sysfixer,0;soacceleratorlib,0;soacceleratorplugin,0;swmanager,0;main,0;trojanscan,0;antivirusGJ,0;drivermanager,0;avhips,0;bd0001,0;patcher,0;attack,0;bdkitUtils,0;android_basic,0;android,0|locksvn,0;rewriteversion,0;rcgen,0;svn,3;prebuild,1;install_defense,1;install_mini,1;sign,1;install_silence,1;build,0;buildtype,2;ignorefault,0;install_combine,0;rebase,0;install,1;install_update,0;pack,1;mashup_installer,1;verify,0;mashup_version,1;send,1;releasesvn,0;symadd,0;xmarkup,0;sendmail,0;verifyinstaller,0;signinstaller,1;commit,1;installermd5,1|markupcode,0|markupdetail,bdm_$revision_$version_$timestamp|prefix,$prefix|v1,1|v2,1|v3,0|v4,489|postfix,$postfix|archive,$share/public/OnlineSetup_GJ/$date_bdm_50|reason,BaiduAn SupplyI|email,sw_xt@baidu.com|supplyid,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001,n50001|codebase,3|cbdetail,HEAD\"}",

             }

def main(argc, argv):
    if argc != 2:
        print 'usage:python cron_client.py <nickname>'
        return
    
    #init logging system, it's told logging is threadsafe, so do NOT need to sync
    logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)

    timeout_buildserver = 0
    opts = list()
    
    while True:
        ws_service = None
        try:
            #make connection to wsserver
            logging.info('try connectting to server')
            ws_service = websocketclt.create_connection("ws://10.52.156.21:13412/buildserver",
                                timeout = timeout_buildserver,
                                sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                                header = opts)
            logging.info('cron-client connected')
        
            #ws_service.send('{"msrc":"ws-client-connect","content":""}')
            
            logging.info('build nickname : %s' % argv[1])
            if cron_tasks.has_key(argv[1]):
                logging.info('build command : %s' % cron_tasks[argv[1]])
                ws_service.send(cron_tasks[argv[1]])
                logging.info('message sent, program quit')
                break
            else:
                logging('can not find specific build nickname, program quit')
        
        except Exception,e:
            logging.error(e)
            time.sleep(5)
    
    logging.info('main quit')

if __name__ == "__main__":
    sys.exit(main(len(sys.argv),sys.argv))
