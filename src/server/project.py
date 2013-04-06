# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	工程配置信息
    
@brief
    project configuration
"""

#总的工程根目录
sln_root = '../../'

#sln名称，介绍，负责人，目录，受哪些工程依赖
bdkv_slns = [
	['commonlib','公共lib库','刘恒','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
]

bdm_slns = [
	['commonlib','公共lib库','刘恒','common_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['skin','公共皮肤库','王超','skin_proj',[]],
	['logicmisc','产品中间层组件','杨彦召','client_proj',['commondll','skin','logicmisc','client','commondll','avcommon','filemon','avhips','drivermanager','sysrepair','antivirus','bdkv','bd0001']],
	['logicutils','通用功能组件','杨彦召','client_proj',[]]
]

projects = {
	'X光':bdkv_slns,
	'极光':bdm_slns,
}