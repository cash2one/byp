import os,sys

cron_tasks = {
             mgr_full_without_tag : "{\"msrc\":\"ws-btn-build\",\"content\":\"d160ad29-80d3-4b22-95a1-61535d14e8ac|极光|commonlib,1;commondll,1;skin,1;logicmisc,1;logicutils,1;client,1;syscleaner,1;soacceleratorplugin,1;swmanager,1;main,1;trojanscan,1;antivirusGJ,1;drivermanager,1;avhips,1;bd0001,1|svn,3;prebuild,2;locksvn,0;rewriteversion,1;buildtype,3;sign,1;ignorefault,1;build,2;install,1;pack,1;symadd,1;signinstaller,1;send,1;releasesvn,0;commit,1|markupcode,0|markupdetail,byp_$r_$v_$t|reason,daily build|email,sw@baidu.com|codebase,3|cbdetail,code base[optional]\"}",
             mgr_full_with_tag : "{\"msrc\":\"ws-btn-build\",\"content\":\"d160ad29-80d3-4b22-95a1-61535d14e8ac|极光|commonlib,1;commondll,1;skin,1;logicmisc,1;logicutils,1;client,1;syscleaner,1;soacceleratorplugin,1;swmanager,1;main,1;trojanscan,1;antivirusGJ,1;drivermanager,1;avhips,1;bd0001,1|svn,3;prebuild,2;locksvn,0;rewriteversion,1;buildtype,3;sign,1;ignorefault,1;build,2;install,1;pack,1;symadd,1;signinstaller,1;send,1;releasesvn,0;commit,1|markupcode,2|markupdetail,byp_$r_$v_$t|reason,daily build|email,sw@baidu.com|codebase,3|cbdetail,code base[optional]\"}",
             
             }

def main(argc, argv):
    if argc != 2:
        print 'usage:python cron_client.py <nickname>'
        return
    
    #init logging system, it's told logging is threadsafe, so do NOT need to sync
    logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
    
    while True:
        ws_service = None
        try:
            #make connection to wsserver
            logging.info('try connectting to server')
            ws_service = websocketclt.create_connection("ws://172.17.180.61:13412/buildserver",
                                timeout = timeout_buildserver,
                                sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                                header = opts)
            logging.info('cron-client connected')
        
            ws_service.send('{"msrc":"ws-client-connect","content":""}')
            
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
