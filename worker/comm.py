# coding=UTF-8
"""
@date 2011-12-15
@brief common function 
@author orz
"""
def saveFile(fname, ctx):
    f=open(fname,"w")
    f.write(ctx)
    f.close()

def getMsg(fname):
    f=open(fname,"r")
    ret = f.read()
    f.close()
    return ret

def getFileBuf(fname):
    f = open(fname,'rb')
    ret = f.read()
    f.close()
    return ret
