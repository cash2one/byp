
#各种字符串宏定义

;xindeng - 多语言支持的字符串定义
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_RESERVEFILE_LANGDLL

#为清理快捷方式添加(中文能删除英文，英文下其实无效)
!define    PRODUCT_LINK_NAME_CH     "百度杀毒"

!define MACRO_PRODUCTNAME          "百度杀毒"

!define MACRO_PRODUCT_FOLDER_NAME  "百度杀毒"

#为清理快捷方式添加
!define PRODUCT_GROUP_EN            "Baidu"
!define PRODUCT_GROUP_CH            "百度软件"

!define MACRO_PRODUCTGROUP          "百度软件"

!define MACRO_COMPANYNAME           "百度在线网络技术（北京）有限公司"

!define MACRO_LNKUBORWSER           "百度杀毒"

!define MACRO_INVALIDDIRECTORY      "您所选的路径不存在，请您重新选择"


!define MACRO_MESSAGEBOX_BTN_OK		"确定" 

!define MACRO_MESSAGEBOX_BTN_CANCLE		"取消" 

!define MACRO_DIRECTORY_ERROR		"您选择的目录不能安装或剩余空间不足，请选择其他安装目录"

!define MACRO_NOENOUGHFREESPACE     "您所选择的路径空间不足，请您重新选择"

!define MACRO_BEGINDELETEOLDVERSION "正在删除历史版本，请等待..."

!define MACRO_BEGINMOVEVERSIONFILE  "正在从临时目录拷贝文件，请等待..."

!define MACRO_BEGINDELETECURVERSION "正在安装"

!define MACRO_LNKUNINSTALL          "卸载百度杀毒"

!define MACRO_MESSAGENOTSUPPORTEDOS "对不起，此版本只支持Windows2000或以上版本的操作系统。"

!define MACRO_MSGFINISHPAGETITLE    "安装完成"

!define MACRO_MESSAGETHANKS         "感谢您使用！"

!define MACRO_TEXTFINISH            "完成"

!define MACRO_MESSAGE64NOTSUPPORT_EN "对不起，暂时不支持64位操作系统"

!define MACRO_MESSAGENOTADMIN       "对不起，非管理员权限无法安装浏览器"

!define MACRO_MESSAGEALREADYRUN     "安装程序已经在运行"

#!define MACRO_MESSAGESAMEVERSION    "您已经安装了百度杀毒，是否继续安装？"

!define MACRO_MESSAGESAMEVERSIONNOQUERY "您已经安装了该版本浏览器"

!define MACRO_MESSAGENEEDREBOOT         "您上次进行的安装或卸载操作需要重启计算机才能完成，请在重启计算机之后再进行新的安装卸载操作。现在是否重启？"

!define MACRO_MESSAGENEEDREBOOTNOQUERY  "您上次进行的安装或卸载操作需要重启计算机才能完成，请在重启计算机之后再进行新的安装卸载操作。"

!define MACRO_MESSAGEUNINSTALL          "您确实要完全移除“$(^Name)”，及其所有的组件？"

#!define MACRO_MESSAGEOLDVERSION         "您已安装了更高版本的百度杀毒$\n确定要安装较低版本吗？"

!define MACO_MESSAGE_SYSTEMCOMPATIBLE	 "您的电脑系统与百度杀毒不能完美兼容，您确定要继续安装？"

!define MACRO_MESSAGEOLDVERSIONNOQUERY  "您的系统已经装有更高版本的百度杀毒，确定要继续安装？"

!define MACRO_MESSAGEOLDVERSION_SAME      "您已安装相同版本的百度杀毒$\n确定要继续安装吗？"

#!define MACRO_MESSAGEOLDVERSIONNOQUERY_SAME "您已安装相同版本的百度杀毒$\n确定要继续安装吗"

!define MACRO_MESSAGE_CLOSE_BROWSER_TIPS "检测到当前百度杀毒正在运行，点击“是”关闭浏览器并继续安装"

!define MACRO_MESSAGE_UNINSTALL_CLOSE_BROWSER_TIPS "检测到当前百度杀毒正在运行，点击“是”关闭浏览器并继续卸载"

#意见反馈页面的标题
!define MACRO_UNINSTALL_REASON_TITLE    "选择卸载原因"

!define MACRO_UNINSTALL_REASON_SUB_HEAD "选择卸载"

!define MACRO_UNINSTALL_REASON_SUB_TAIL "的原因"

!define MACRO_BEGINCHECKSSO             "检测统一登录插件"

!define MACRO_CHECKDEAFULTBROWSER       "设置为默认浏览器"

!define MACRO_CHECKRUNNOW               "立即运行"

!define MACRO_LNKUNINSTALL_TIPS         "这个向导将从您的计算机卸载百度杀毒, 单击[卸载(U)]开始卸载进程。"

!define MACRO_UNINSTALL_DIRTXT          "卸载目录"

!define MACRO_UNINSTALL_APP_CHECK       "同时删除您本机的收藏夹、历史记录和个人配置等数据"

!define MACRO_MESSAGEINSTALL_WARNING  	"检测到当前程序正在运行,是否强制结束并安装?"

!define MACRO_MESSAGEUNINSTALL_WARNING  "检测到当前程序正在运行,是否强制结束并卸载?"

!define MACRO_ANTIVIRUS_UPDATETIME  	"2013.04.05 1216"

!define MACRO_SHORTCUT_DESCRIPTION		"百度杀毒，安全可依赖"