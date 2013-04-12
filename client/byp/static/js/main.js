//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

var worker = undefined;

String.format = function ()
{
    var param = [];
    for (var i = 0, l = arguments.length; i < l; i++)
    {
        param.push(arguments[i]);
    }
    var statment = param[0]; // get the first element(the original statement)
    param.shift(); // remove the first element from array
    return statment.replace(/\{(\d+)\}/g, function(m, n)
    {
        return param[n];
    });
}

//初始化UI
function initUI() {
    //初始化combobox
    $('.combobox').combobox();

    //初始化tooltip功能
    $(function () {
        $("[rel='tooltip']").tooltip();
    });

    //初始化typeahead功能
    $('.typeahead').typeahead()

    //更改tooltip颜色
    //$('a.tooltip-colorfy').hover(function() {changeTooltipColorTo('#f00')});

    //重新计算输出框的height，为了fit整个的height=550px
    var hTotal = $(window).height();
    var h1 = $("#table-build-config").height();
    var h2 = $("#table-build-info").height();
    var h3 = $("#table-build-depend").height();
    var h4 = $("#table-progress-info").height();
    var h5 = $("#table-status-info").height();
    $("#ws-build-log").height(hTotal - h1 - h2 - h3 - h4 - h5 - 65);

}

$(document).ready(function() {
    //初始化UI
    initUI();

    //定制默认按钮按下行为
    //$('.btn-group > .btn, .btn[data-toggle="button"]').bind('click',onInverseBtnClick);
    //buildall按钮按下行为
    $("#ws-sln-buildall").bind('click',onBuildallBtnClick);

    //绑定默认project和worker选择事件
    $('#ws-project-select').bind('change',onProjectSelect);
    $('#ws-worker-select').bind('change',onWorkerSelect);
    //绑定input text默认事件
    $('#ws-cb-detail,#ws-build-reason,#ws-user-email').bind('click',onInputClick);
    //初始化typeahead
    $('#ws-cb-detail,#ws-build-reason,#ws-user-email').typeahead();
    //初始化build按钮
    $("#ws-btn-build").bind('click',onBtnBuildClick);

    //激活默认build depends
    $("#btn-revision-build-depend").click();
    //默认激活build all
    $("#ws-sln-buildall").click();

    //start backend communication worker
    worker = new Worker("static/js/worker.js");
    worker.onmessage = function(evt) {
        updateUI(evt.data)
    };
    
});

function onBtnBuildClick() {
    var ctx = "";
    //proj name
    ctx += $("#ws-project-select option:selected").text();
    ctx += "|";
    //sln list
    $(".btn[id^='ws-btn-slnselect-']").each( function() {
        if ($(this).hasClass("active")) {
            ctx += String.format("{0},1;",$(this).children().html());
        }
        else {
            ctx += String.format("{0},0;",$(this).children().html());   
        }
    });
    ctx = ctx.slice(0,-1);
    ctx += "|"
    //build options
    $(".btn[id^='ws-btn-option-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).children().attr('value') == undefined) {
                ctx += String.format("{0},1;",$(this).children().attr('name'));
            }
            else {
                ctx += String.format("{0},{1};",$(this).children().attr('name'),$(this).children().attr('value'));
            }
        }
    })
    ctx = ctx.slice(0,-1);
    ctx += "|"
    //build-reason and user-email
    ctx += String.format("reason,{0}|",$("#ws-build-reason").attr('value'));
    ctx += String.format("email,{0}|",$("#ws-user-email").attr('value'));
    //codebase
    $(".btn[id^='ws-btn-codebase-']").each( function() {
        if ($(this).hasClass("active")) {
            ctx += String.format("codebase,{0}",$(this).attr('value'));
        }
    })
    alert(ctx);
    var msg = formatMessage("ws-btn-build",ctx);
    worker.postMessage(msg);
}

function onInputClick() {
    $(this).select();
}

function updateUI(msg) {
    //$("#ws-build-log").append(msg);
    //$("#ws-build-log").append('<br>');

    var jsonMsg = JSON.parse(msg)
    //更新项目combobox
    if (jsonMsg['msrc'] == "ws-project-select") {
        //清空project项目
        $("#ws-project-select").empty();

        var projs = jsonMsg['content'].split(",");
        for (var index in projs) {
            var node = String.format("<option value=\"{0}\">{1}</option>",projs[index],projs[index]);
            $("#ws-project-select").append(node);
        }
        $("#ws-project-select").change();
    }
    //更新sln按钮们
    else if (jsonMsg['msrc'] == "ws-sln-select") {
        var sln = jsonMsg['content'].split(",");
        var slnName = sln[0];
        var slnTooltip = String.format("{0},责任人:{1}",sln[1],sln[2]);
        var btnId = "ws-btn-slnselect-" + randomChar(32);
        var node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\">{2}</a></button>&nbsp;",btnId,slnTooltip,slnName);
        $("#ws-sln-select-" + sln[3]).append(node);
        $("#"+btnId).bind('click',onSlnBtnClick);
        $("#"+btnId).click();
    }
    //更新build options
    else if (jsonMsg['msrc'] == 'ws-build-options') {
        var ctx = jsonMsg['content'].split("|");
        if (ctx[1] == 'check') {
            var info = ctx[3].split(",");
            var btnId = "ws-btn-option-" + randomChar(32);
            var node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\"title=\"{2}\">{3}</a></button>&nbsp;",btnId,ctx[0],info[1],info[0]);
            $("#ws-build-options-" + ctx[2]).append(node);
            $("#"+btnId).bind('click',onInverseBtnClick);
            $("#"+btnId).click();
        }
        else if (ctx[1] == 'radio') {
            var arr = new Array();
            var arrActive = new Array();
            var btnId = "ws-btn-option-" + randomChar(32);
            var node = String.format("<div id=\"{0}\" class=\"btn-group\" data-toggle=\"buttons-radio\">",btnId);
            arr.push(btnId);
            var info = ctx[3].split(";");
            for (var index in info) {
                var items = info[index].split(",");
                var btnId = "ws-btn-option-" + randomChar(32);
                var option = "";
                if (items.length == 4 && items[3] == 'default') {
                    var option = String.format("<button type=\"button\" id=\"{0}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\" title=\"{2}\" value=\"{3}\">{4}</a></button>",btnId,ctx[0],items[1],items[2],items[0]);
                    arrActive.push(btnId);
                }
                else {
                    option = String.format("<button type=\"button\" id=\"{0}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\" title=\"{2}\" value=\"{3}\">{4}</a></button>",btnId,ctx[0],items[1],items[2],items[0]);
                }
                
                node += option;
                arr.push(btnId);
            }
            node += "</div>&nbsp;"
            $("#ws-build-options-" + ctx[2]).append(node);
            for (var index in arr) {
                $("#"+arr[index]).bind('click',onInverseBtnClick);
            }
            for (var index in arrActive) {
                $("#"+arrActive[index]).click();
            }
        }
    }
    //更新代码基radiobutton
    else if (jsonMsg['msrc'] == 'ws-code-base') {
        var items = jsonMsg['content'].split(",");
        var btnId = "ws-btn-codebase-" + randomChar(32);
        var activeBtnId = ''
        var node = String.format("<button type=\"button\" id=\"{0}\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
        if (items.length == 4 && items[3] == 'default') {
            activeBtnId = btnId;
        }
        $("#ws-code-base").append(node);
        $("#"+btnId).bind('click',onInverseBtnClick);
        $("#"+activeBtnId).click();
    }
    //更新worker combobox
    else if (jsonMsg['msrc'] == 'ws-worker-select') {
        var worker = jsonMsg['content'].split(",");
        if (worker[0] == 'add') {
            var node = String.format("<option id=\"{0}\" class=\"{1}\" value=\"{2}\">{3}</option>",worker[1],worker[3],worker[4],worker[2]);    
            $("#ws-worker-select").append(node);
        }
        else if (worker[0] == 'remove') {
            $("#"+worker[1]).remove();
        }
        else if (worker[0] == 'update') {
            var ip = $("#"+worker[1]).attr('value');
            var nickname = $("#"+worker[1]).html();
            $("#"+worker[1]).remove();
            var node = String.format("<option id=\"{0}\" class=\"{1}\" value=\"{2}\">{3}</option>",worker[1],worker[2],ip,nickname);    
            $("#ws-worker-select").append(node);
        }
        //处理默认选择
        updateWorkerStatus();
    }
    //更新worker状态
    else if (jsonMsg['msrc'] == 'ws-worker-running' || jsonMsg['msrc'] == 'ws-worker-idle' || jsonMsg['msrc'] == 'ws-worker-error') {
        var currentVal = parseInt($("#"+jsonMsg['msrc']).html());
        if (jsonMsg['content'] == "+") {
            currentVal += 1;
        }
        else if (jsonMsg['content'] == "-") {
            currentVal -= 1;
        }
        $("#"+jsonMsg['msrc']).html(currentVal.toString());
        
        //处理默认选择
        updateWorkerStatus();
    }
    //通知client重新注册ui
    else if (jsonMsg['msrc'] == 'ws-client-update') {
        //重新初始化UI
        initUI();
    }
    //更新build log
    else if (jsonMsg['msrc'] == 'ws-build-log') {
        $("#ws-build-log").append(jsonMsg['content']);
        $("#ws-build-log").append('<br>');
    }
    else if (jsonMsg['msrc'] == 'ws-build-progress') {
        $("#ws-build-progress").attr("style","width:"+jsonMsg['content']+"%;");
        $("#ws-build-progress-text").text(jsonMsg['content']+"%");
    }
}

//生成随机字符串
function  randomChar(length) {
    var x="0123456789qwertyuioplkjhgfdsazxcvbnm";
    var tmp="";
    for(var i=0;i<length;i++)  {
        tmp += x.charAt(Math.ceil(Math.random()*100000000)%x.length);
    }
    return  tmp;
}

//checkbox color change action
function onInverseBtnClick() {
    //common
    if($(this).attr('class-toggle') != undefined && !$(this).hasClass('disabled')){
        var btnGroup = $(this).parent('.btn-group');

        if(btnGroup.attr('data-toggle') == 'buttons-radio') {
            btnGroup.find('.btn').each(function() {
                $(this).removeClass($(this).attr('class-toggle'));
            });
            $(this).addClass($(this).attr('class-toggle'));
        }

        if(btnGroup.attr('data-toggle') == 'buttons-checkbox' || $(this).attr('data-toggle') == 'button') {
            if($(this).hasClass('active')) {
                $(this).removeClass($(this).attr('class-toggle'));
            } else {
                $(this).addClass($(this).attr('class-toggle'));
            }
        }
    }    
}

//sln按钮的默认行为
function onSlnBtnClick() {
    if($(this).attr('class-toggle') != undefined && !$(this).hasClass('disabled')){
        var btnGroup = $(this).parent('.btn-group');

        if(btnGroup.attr('data-toggle') == 'buttons-radio') {
            btnGroup.find('.btn').each(function() {
                $(this).removeClass($(this).attr('class-toggle'));
            });
            $(this).addClass($(this).attr('class-toggle'));
        }

        if(btnGroup.attr('data-toggle') == 'buttons-checkbox' || $(this).attr('data-toggle') == 'button') {
            if($(this).hasClass('active')) {
                $(this).removeClass($(this).attr('class-toggle'));
            } else {
                $(this).addClass($(this).attr('class-toggle'));
            }
        }
    }    
}

//buildall按钮默认行为
function onBuildallBtnClick() {
    //common
    if($(this).attr('class-toggle') != undefined && !$(this).hasClass('disabled')){
        var btnGroup = $(this).parent('.btn-group');

        if(btnGroup.attr('data-toggle') == 'buttons-radio') {
            btnGroup.find('.btn').each(function() {
                $(this).removeClass($(this).attr('class-toggle'));
            });
            $(this).addClass($(this).attr('class-toggle'));
        }

        if(btnGroup.attr('data-toggle') == 'buttons-checkbox' || $(this).attr('data-toggle') == 'button') {
            if($(this).hasClass('active')) {
                $(this).removeClass($(this).attr('class-toggle'));
                $(".btn[id^='ws-btn-slnselect']").each( function() {
                    if ($(this).hasClass("active")) {
                        $(this).click();
                    }
                });
            } else {
                $(this).addClass($(this).attr('class-toggle'));
                $(".btn[id^='ws-btn-slnselect']").each( function() {
                    if (!$(this).hasClass("active")) {
                        $(this).click();
                    }
                });
            }
        }
    }    
}

//点击更换项目
function onProjectSelect() {
    //清空sln项目和build-options
    $("#ws-sln-select-base").empty();
    $("#ws-sln-select-base").append("<span class=\"label label-success\">公共类库</span>&nbsp;");
    $("#ws-sln-select-middle").empty();
    $("#ws-sln-select-middle").append("<span class=\"label label-success\">中间层组件</span>&nbsp;");
    $("#ws-sln-select-module").empty();
    $("#ws-sln-select-module").append("<span class=\"label label-success\">功能模块</span>&nbsp;");
    $("#ws-build-options-before").empty();
    $("#ws-build-options-before").append("<span class=\"label label-success\">打包前选项</span>&nbsp;");
    $("#ws-build-options-build").empty();
    $("#ws-build-options-build").append("<span class=\"label label-success\">构造选项</span>&nbsp;");
    $("#ws-build-options-after").empty();
    $("#ws-build-options-after").append("<span class=\"label label-success\">打包后选项</span>&nbsp;");
    //清空build-depends
    $("#ws-code-base").empty();

    var currentSel = $("#ws-project-select option:selected").text();
    var msg = formatMessage("ws-sln-select",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-build-options",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-code-base",currentSel);
    worker.postMessage(msg);
}

function updateWorkerStatus() {
    $("#ws-worker-status").removeClass();
    $("#ws-worker-detail").removeClass();

    var cls = $("#ws-worker-select option:selected").attr('class');
    var ip = $("#ws-worker-select option:selected").attr('value');
    
    if (cls == undefined || ip == undefined) {
        $("#ws-worker-status").text("None");
        $("#ws-worker-status").addClass("label label-warning");
        $("#ws-worker-detail").addClass("label label-warning");
        $("#ws-worker-detail").text("目前没有在线的编译机");
    }
    else {
        $("#ws-worker-status").text(ip);
        if (cls == "running") {
            $("#ws-worker-status").addClass("label label-success");
            $("#ws-worker-detail").addClass("label label-success");
            $("#ws-worker-detail").text("系统当前正在打包，请稍等...");
        }
        else if (cls == "idle") {
            $("#ws-worker-status").addClass("label");
            $("#ws-worker-detail").addClass("label label");
            $("#ws-worker-detail").text("该编译机当前空闲");
        }
        else if (cls == "error") {
            $("#ws-worker-status").addClass("label label-important");
            $("#ws-worker-detail").addClass("label label-important");
            $("#ws-worker-detail").text("该编译机出现错误");
        }
    }
}

//切换worker响应
function onWorkerSelect() {
    //清空日志输出区域
    $("#ws-build-log").empty();

    updateWorkerStatus();
}


function formatMessage(msrc,content) {
    var msg = String.format("{\"msrc\":\"{0}\",\"content\":\"{1}\"}",msrc,content);
    return msg;
}

//change tooltip background color
function changeTooltipColorTo(color) {
    $('.tooltip-inner').css('background-color', color)
    $('.tooltip.top .tooltip-arrow').css('border-top-color', color);
    $('.tooltip.right .tooltip-arrow').css('border-right-color', color);
    $('.tooltip.left .tooltip-arrow').css('border-left-color', color);
    $('.tooltip.bottom .tooltip-arrow').css('border-bottom-color', color);
}
