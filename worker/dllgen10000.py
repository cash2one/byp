# encoding UTF-8

'''

策略为保持有动态的10000个dll可用，对每个目录的混淆dll都是如此
每次每个目录打100个，跳到下个目录，迭代到10000后重置

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
