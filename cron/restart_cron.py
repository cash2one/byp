# coding=UTF-8

import os
import sys
import subprocess
import logging
import argparse
import sconf

def main(argc,argv):
    #init logging system, it's told logging is threadsafe, so do NOT need to sync
    logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)

    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r','--restart-host', action='store', default='', dest='restartHost', help='build host to restart with')
    args = parser.parse_args()
    logging.info('restartHost : ' + args.restartHost)
    
    restart_scripts = []
    if sconf.host_script_map.has_key(args.restartHost):
        restart_scripts = sconf.host_script_map[args.restartHost]
    
    if len(restart_scripts) == 0:
        return

    #end all python process, will be executed by bat
    #command = 'taskkill /F /IM python.exe'
    #os.system(command)

    #start specific scripts
    for item in restart_scripts:
        print item
        subprocess.Popen('cmd /c start python.exe ' + item)



if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))
