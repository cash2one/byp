# encoding UTF-8

'''


'''
import code_confusion_aladdin
import code_confusion_aladdin_adapt
import code_confusion_aladdin_adapt_bdm
import code_confusion_bdm
import code_confusion_bdm_combine
import code_confusion_combine
import code_confusion_pacific

nFunc = 256
nNum = 100
nStart = 0
while True:
    nStart = 0
    for loop in range(0,100):
        nStart = nStart + loop * nNum
        code_confusion_aladdin.generate(nFunc, nNum, nStart)
        code_confusion_bdm.generate(nFunc, nNum, nStart)
        code_confusion_pacific.generate(nFunc, nNum, nStart)
        code_confusion_bdm_combine.generate(nFunc, nNum, nStart)
        code_confusion_combine.generate(nFunc, nNum, nStart)
        code_confusion_aladdin_adapt.generate(nFunc, nNum, nStart)
        code_confusion_aladdin_adapt_bdm.generate(nFunc, nNum, nStart)
