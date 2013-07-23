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
    $("[rel='tooltip']").tooltip();

    //初始化typeahead功能
    $('.typeahead').typeahead()

    //重新计算输出框的height，为了fit整个的height=550px
    var hTotal = $(window).height();
    if (hTotal < 595)
        hTotal = 595;
    var h0 = $("#table-installer-info").height();
    var h1 = $("#table-build-config").height();
    var h2 = $("#table-build-info").height();
    var h3 = $("#table-build-depend").height();
    var h4 = $("#table-progress-info").height();
    var h5 = $("#table-status-info").height();
    var h6 = $("#table-markup-code").height();

    var left = hTotal - h0 - h1 - h2 - h3 - h4 - h5 - h6 - 65;
    $("#ws-build-log").height(left);
}

$(document).ready(function() {
    //初始化UI
    initUI();

    //定制默认按钮按下行为
    //$('.btn-group > .btn, .btn[data-toggle="button"]').bind('click',onInverseBtnClick);
    //default project按钮按下行为
    $("#btn-project-default").bind('click',onDefaultBuildBtnClick);
    //default options按钮按下行为
    $("#btn-options-default").bind('click',onDefaultOptionsBtnClick);
    //switch project按钮按下行为
    $("#btn-project-switch").bind('click',onBtnProjectSwitchClick);
    //switch options按钮按下行为
    $("#btn-options-switch").bind('click',onBtnOptionsSwitchClick);

    //绑定默认project和worker选择事件
    $('#ws-project-select').bind('change',onProjectSelect);
    $('#ws-worker-select').bind('change',onWorkerSelect);

    //绑定model页worker切换事件
    $('#ws-model-worker-select').bind('change',onModelWorkerSelect);

    //绑定model-select切换和model-name-select事件
    $('#ws-model-category-select').bind('change',onModelCategorySelect);
    $('#ws-model-name-select').bind('change',onModelNameSelect);
    
    //绑定input text默认事件
    $('#ws-model-name,#ws-model-description,#ws-model-remark,#ws-installer-archive,#ws-build-reason,#ws-user-email,#ws-cb-detail,#ws-build-prefix,#ws-build-postfix,#ws-build-v1,#ws-build-v2,#ws-build-v3,#ws-build-v4,#ws-installer-supplyid,#ws-markup-detail').bind('click',onInputClick);
    //初始化typeahead
    $('#ws-installer-archive,#ws-build-reason,#ws-user-email,#ws-cb-detail,#ws-build-prefix,#ws-build-postfix,#ws-build-v1,#ws-build-v2,#ws-build-v3,#ws-build-v4,#ws-installer-supplyid,#ws-markup-detail').typeahead();
    //初始化build按钮
    $("#ws-btn-build").bind('click',onBtnBuildClick);
    //初始化model按钮
    $("#ws-btn-model").bind('click',onBtnModelClick);
    //初始化log-tab按下事件
    $('a[data-toggle="tab"]').bind('shown', onLogTabClick)
    //模版删除按钮事件
    $("#btn-model-delete").bind('click',onBtnModelDelete);
    //模板激活按钮事件
    $("#btn-model-activate").bind('click',onBtnModelActivate);

    //start backend communication worker
    worker = new Worker("static/js/worker.js");
    worker.onmessage = function(evt) {
        updateUI(evt.data)
    };
    
});

function onBtnModelDelete() {
    var modelMsg = "";
    var modelCategory = $("#ws-model-category-select option:selected").text();
    modelMsg += String.format("{0}|",modelCategory);
    var modelName = $("#ws-model-name-select option:selected").text();
    modelMsg += String.format("{0}",modelName);

    g_bFirstDelete = true;
    $("#btn-delete-model-confirm").bind('click',function() {
        if (g_bFirstDelete) {
            //alert(modelMsg);
            var msg = formatMessage("ws-model-delete",modelMsg);
            worker.postMessage(msg);
            g_bFirstBuild = false;   
        }
    })
    $("#deleteConfirmModal").modal();
}

function onBtnModelActivate() {
    var modelMsg = "";
    var modelCategory = $("#ws-model-category-select option:selected").text();
    modelMsg += String.format("{0}|",modelCategory);
    var modelName = $("#ws-model-name-select option:selected").text();
    modelMsg += String.format("{0}",modelName);
    
    var msg = formatMessage("ws-model-activate",modelMsg);
    worker.postMessage(msg);
}

function onLogTabClick(e) {
    if ($(e.target).attr('href') == '#tabLog') {
        $("#ws-build-log2").scrollTop(document.getElementById('ws-build-log2').scrollHeight)
    }
    else if ($(e.target).attr('href') == '#tabTemplate') {
        var msg = formatMessage("ws-update-category","");
        worker.postMessage(msg);
    }
    else if ($(e.target).attr('href') == '#tabMain') {
        initUI();
    }
}

function getConfiguration() {
    var idleWorker = $("#ws-worker-idle").text()
    var errorWorker = $("#ws-worker-error").text()
    if (idleWorker == '0' && errorWorker == '0') {
        alert("~当前没有空闲编译机，请等待当前打包完成~");
        return ["",false,false,false];
    }

    ctx = "";
    var defaultProjChanged = false;
    var defaultOptionChanged = false;
    var defaultCbChanged = false;
    //worker id
    ctx += $("#ws-worker-select option:selected").attr('id');
    ctx += "|";
    //proj name
    ctx += $("#ws-project-select option:selected").text();
    ctx += "|";
    //sln list
    $(".btn[id^='ws-btn-slnselect-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                defaultPorjChanged = true;
            }
            ctx += String.format("{0},1;",$(this).children().html());
        }
        else {
            if ($(this).attr('default') == 'true') {
                defaultProjChanged = true;
            }
            ctx += String.format("{0},0;",$(this).children().html());   
        }
    });
    ctx = ctx.slice(0,-1);
    ctx += "|"
    //build options
    $(".btn[id^='ws-btn-option-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                defaultOptionChanged = true;
            }
            if ($(this).children().attr('value') == undefined) {
                ctx += String.format("{0},1;",$(this).children().attr('name'));
            }
            else {
                ctx += String.format("{0},{1};",$(this).children().attr('name'),$(this).children().attr('value'));
            }
        }
        else {
            if ($(this).attr('default') == 'true') {
                defaultOptionChanged = true;
            }
            if ($(this).children().attr('value') == undefined) {
                ctx += String.format("{0},0;",$(this).children().attr('name'));
            }
        }
    })
    ctx = ctx.slice(0,-1);
    ctx += "|";
    //markup-code
    $(".btn[id^='ws-btn-markup-code-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                defaultCbChanged = true;
            }
            ctx += String.format("markupcode,{0}|",$(this).attr('value'));
        }
    })
    ctx += String.format("markupdetail,{0}",document.getElementById("ws-markup-detail").value);
    ctx += "|";

    //build version
    var prefix = document.getElementById("ws-build-prefix").value;
    var v1 = document.getElementById("ws-build-v1").value;
    if(!v1.match(/^[0-9]+$/)){
        alert("版本号必须输入非负整数。");
        $("#ws-build-v1").focus();
        $("#ws-build-v1").select();
        return ["",false,false,false];
    }
    var v2 = document.getElementById("ws-build-v2").value;
    if(!v2.match(/^[0-9]+$/)){
        alert("版本号必须输入非负整数。");
        $("#ws-build-v2").focus();
        $("#ws-build-v2").select();
        return ["",false,false,false];
    }
    var v3 = document.getElementById("ws-build-v3").value;
    if(!v3.match(/^[0-9]+$/)){
        alert("版本号必须输入非负整数。");
        $("#ws-build-v3").focus();
        $("#ws-build-v3").select();
        return ["",false,false,false];
    }
    var v4 = document.getElementById("ws-build-v4").value;
    if(!v4.match(/^[0-9]+$/) && v4 != "$auto"){
        alert("版本号必须输入非负整数。");
        $("#ws-build-v4").focus();
        $("#ws-build-v4").select();
        return ["",false,false,false];
    }
    var postfix = document.getElementById("ws-build-postfix").value;

    ctx += String.format("prefix,{0}|",prefix);
    ctx += String.format("v1,{0}|",v1);
    ctx += String.format("v2,{0}|",v2);
    ctx += String.format("v3,{0}|",v3);
    ctx += String.format("v4,{0}|",v4);
    ctx += String.format("postfix,{0}|",postfix);

    //installer archive
    var archive = document.getElementById("ws-installer-archive").value;
    ctx += String.format("archive,{0}|",archive)

    //build-reason and user-email
    var reason = document.getElementById("ws-build-reason").value;
    if (reason.length > 15) {
        reason = reason.substring(0,15);
    }
    if(reason == ''){
        alert("请输入打包原因。");
        $("#ws-build-reason").focus();
        return ["",false,false,false];
    }
    var email = document.getElementById("ws-user-email").value
    if (email.length > 30) {
        email = email.substring(0,30);
    }
    if(!email.match(/^\w+((-\w+)|(\.\w+))*\@baidu.com$/)){
        alert("百度邮箱格式不正确，请重新输入。");
        $("#ws-user-email").focus();
        $("#ws-user-email").select();
        return ["",false,false,false];
    }
    ctx += String.format("reason,{0}|",reason);
    ctx += String.format("email,{0}|",email);

    //supplyid
    var supplyid = document.getElementById("ws-installer-supplyid").value;
    sids = supplyid.split(',');
    for (var i in sids){
        if (!sids[i].match(/^[mnf]\d{1,}$/) && sids[i] != "") {
            alert("supplyid格式不正确，请重新输入。")
            $("#ws-installer-supplyid").focus();
            $("#ws-installer-supplyid").select();
            return ["",false,false,false];
        };
    }
    ctx += String.format("supplyid,{0}|",supplyid);
    //codebase
    $(".btn[id^='ws-btn-codebase-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                defaultCbChanged = true;
            }
            ctx += String.format("codebase,{0}|",$(this).attr('value'));
        }
    })
    ctx += String.format("cbdetail,{0}",document.getElementById("ws-cb-detail").value);
    return [ctx,defaultProjChanged,defaultOptionChanged,defaultCbChanged];
}

function onBtnModelClick() {
    ctx = getConfiguration();
    if (ctx[0] == "") {
        return;
    }
    g_bFirstModel = true;
    $("#btn-model-confirm").bind('click',function() {
        if (g_bFirstModel) {
            var modelMsg = "";
            var product = $("#ws-project-select option:selected").text();
            modelMsg += String.format("{0}|",product);
            if ($("#ws-model-category option:selected").hasClass("default")) {
                alert("必须选择模板类别");
                return;
            }
            var modelCategory = $("#ws-model-category option:selected").text();
            modelMsg += String.format("{0}|",modelCategory);
            var modelName = $("#ws-model-name").val();
            if (modelName == "") {
                alert("必须输入模板名称。");
                $("#ws-model-name").focus();
                $("#ws-model-name").select();
                return;
            }
            var reg=new RegExp("\n","g");
            modelMsg += String.format("{0}|",modelName);
            modelMsg += String.format("{0}|",$("#ws-model-description").val().replace(reg,"<br>"));
            modelMsg += String.format("{0}^",$("#ws-model-remark").val().replace(reg,"<br>"));
            modelMsg += String.format("{0}",ctx[0]);
            //alert(modelMsg);
            var msg = formatMessage("ws-btn-model",modelMsg);
            worker.postMessage(msg);

            //切换到模板页
            $(".nav-pills").children().removeClass("active");
            $(".tab-content").children().removeClass("active");
            $("#tabTemplate-title").addClass("active");
            $("#tabTemplate").addClass("active");
            var msg = formatMessage("ws-update-category","");
            worker.postMessage(msg);
            
            g_bFirstModel = false;   
        }
    })
    $("#modelAddConfirm").modal();
}

function onBtnBuildClick() {
    ctx = getConfiguration();
    if (ctx[0] == "") {
        return;
    }
    g_bFirstBuild = true;
    $("#btn-build-confirm, #btn-common-build-confirm").bind('click',function() {
        if (g_bFirstBuild) {
            //alert(ctx[0]);
            var msg = formatMessage("ws-btn-build",ctx[0]);
            worker.postMessage(msg);
            g_bFirstBuild = false;   
        }
    })
    if (ctx[1] || ctx[2] || ctx[3]) {
        $("#defaultOptionChangedModal").modal();
    }
    else {
        $("#buildConfirmModal").modal();
    }
}

function onInputClick() {
    $(this).select();
}

function updateUI(msg) {

    var jsonMsg = JSON.parse(msg)
    //更新项目combobox
    if (jsonMsg['msrc'] == "ws-project-select") {
        //清空project项目
        $("#ws-project-select").empty();

        var projs = jsonMsg['content'].split("|");
        for (var index in projs) {
            var node = String.format("<option value=\"{0}\">{1}</option>",projs[index],projs[index]);
            $("#ws-project-select").append(node);
        }
        $("#ws-project-select").change();
    }
    //更新sln按钮们
    else if (jsonMsg['msrc'] == "ws-sln-select") {
        var sln = jsonMsg['content'].split("|");
        var slnName = sln[0];
        var slnTooltip = String.format("{0},责任人:{1}",sln[1],sln[2]);
        var btnId = "ws-btn-slnselect-" + randomChar(32);
        var node = '';
        var bDefault = false;
        if (sln.length == 5 && sln[4] == 'default') {
            node = String.format("<button type=\"button\" id=\"{0}\" default=\"true\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\">{2}</a></button>&nbsp;",btnId,slnTooltip,slnName);
            bDefault = true;
        }
        else {
            node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\">{2}</a></button>&nbsp;",btnId,slnTooltip,slnName);
            bDefault = false;
        }
        $("#ws-sln-select-" + sln[3]).append(node);
        $("#"+btnId).bind('click',onSlnBtnClick);
        if (bDefault) {
            $("#"+btnId).click();
        }
    }
    //更新build options
    else if (jsonMsg['msrc'] == 'ws-build-options') {
        var ctx = jsonMsg['content'].split("|");
        var arr = new Array();
        var arrActive = new Array();
        var node = "";
        
        if (ctx[1] == 'check') {
            var info = ctx[3].split(";");
            var btnId = "ws-btn-option-" + randomChar(32);
            if (info.length == 3 && info[2] == 'default') {
                node = String.format("<button type=\"button\" id=\"{0}\" default=\"true\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\"title=\"{2}\">{3}</a></button>&nbsp;",btnId,ctx[0],info[1],info[0]);
                arrActive.push(btnId);
            }
            else {
                node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\"title=\"{2}\">{3}</a></button>&nbsp;",btnId,ctx[0],info[1],info[0]);
            }
            arr.push(btnId);
        }
        else if (ctx[1] == 'radio') {
            var btnId = "ws-btn-option-" + randomChar(32);
            node = String.format("<div id=\"{0}\" class=\"btn-group\" data-toggle=\"buttons-radio\">",btnId);
            arr.push(btnId);
            var info = ctx[3].split(";");
            for (var index in info) {
                var items = info[index].split(",");
                var btnId = "ws-btn-option-" + randomChar(32);
                var option = "";
                if (items.length == 4 && items[3] == 'default') {
                    var option = String.format("<button type=\"button\" id=\"{0}\" default=\"true\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\" title=\"{2}\" value=\"{3}\">{4}</a></button>",btnId,ctx[0],items[1],items[2],items[0]);
                    arrActive.push(btnId);
                }
                else {
                    option = String.format("<button type=\"button\" id=\"{0}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" name=\"{1}\" title=\"{2}\" value=\"{3}\">{4}</a></button>",btnId,ctx[0],items[1],items[2],items[0]);
                }
                
                node += option;
                arr.push(btnId);
            }
            node += "</div>&nbsp;"
        }

        $("#ws-build-options-" + ctx[2]).append(node);
        
        for (var index in arr) {
            $("#"+arr[index]).bind('click',onInverseBtnClick);
        }
        for (var index in arrActive) {
            $("#"+arrActive[index]).click();
        }
    }
    //更新代码基radiobutton
    else if (jsonMsg['msrc'] == 'ws-code-base') {
        var items = jsonMsg['content'].split("|");
        var btnId = "ws-btn-codebase-" + randomChar(32);
        var activeBtnId = ''
        var node = "";
        node = String.format("<button type=\"button\" id=\"{0}\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
        if (items.length == 4 && items[3] == 'default') {
            node = String.format("<button type=\"button\" id=\"{0}\" default = \"true\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
            activeBtnId = btnId;
        }
        else {
            node = String.format("<button type=\"button\" id=\"{0}\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
        }
        $("#ws-code-base").append(node);
        $("#"+btnId).bind('click',onInverseBtnClick);
        $("#"+activeBtnId).click();
    }
    //更新标记代码radiobutton
    else if (jsonMsg['msrc'] == 'ws-markup-code') {
        var items = jsonMsg['content'].split("|");
        var btnId = "ws-btn-markup-code-" + randomChar(32);
        var activeBtnId = ''
        var node = "";
        node = String.format("<button type=\"button\" id=\"{0}\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
        if (items.length == 4 && items[3] == 'default') {
            node = String.format("<button type=\"button\" id=\"{0}\" default = \"true\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
            activeBtnId = btnId;
        }
        else {
            node = String.format("<button type=\"button\" id=\"{0}\" value=\"{1}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{2}\">{3}</a></button>",btnId,items[2],items[1],items[0]);
        }
        $("#ws-markup-code").append(node);
        $("#"+btnId).bind('click',onInverseBtnClick);
        $("#"+activeBtnId).click();
    }
    //更新worker combobox
    else if (jsonMsg['msrc'] == 'ws-worker-select') {
        var worker = jsonMsg['content'].split("|");
        if (worker[0] == 'add') {
            var node = String.format("<option id=\"{0}\" class=\"{1}\" ip=\"{2}\" value=\"{3}\">{4}</option>",worker[1],worker[3],worker[4],worker[2],worker[2]);    
            $("#ws-worker-select").append(node);
            node = String.format("<option id=\"{0}\" class=\"{1}\" ip=\"{2}\" value=\"{3}\">{4}</option>","model-"+worker[1],worker[3],worker[4],worker[2],worker[2]);
            $("#ws-model-worker-select").append(node);
        }
        else if (worker[0] == 'remove') {
            $("#"+worker[1]).remove();
            $("#model-"+worker[1]).remove();
        }
        else if (worker[0] == 'update') {
            var ip = $("#"+worker[1]).attr('value');
            var nickname = $("#"+worker[1]).html();
            $("#"+worker[1]).remove();
            var node = String.format("<option id=\"{0}\" class=\"{1}\" ip=\"{2}\" value=\"{3}\">{4}</option>",worker[1],worker[2],ip,nickname,nickname);    
            $("#ws-worker-select").prepend(node);
            node = String.format("<option id=\"{0}\" class=\"{1}\" ip=\"{2}\" value=\"{3}\">{4}</option>","model-"+worker[1],worker[2],ip,nickname,nickname);    
            $("#ws-model-worker-select").prepend(node);
            $("#"+worker[1]).attr('selected','selected');
            $("#ws-worker-select").val(nickname);
            $("#ws-model-worker-select").val(nickname);
        }
        else if (worker[0] == 'change') {
            var ctx = jsonMsg['content'].split('|');
            var nickname = $("#"+worker[1]).html();
            $("#"+ctx[1]).attr('selected','selected');
            $("#ws-worker-select").val(nickname);
            $("#ws-model-worker-select").val(nickname);
        }
        //处理默认选择
        updateWorkerStatus();
        updateModelWorkerStatus();
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
        
        currentVal = parseInt($("#"+jsonMsg['msrc'] + "-model").html());
        if (jsonMsg['content'] == "+") {
            currentVal += 1;
        }
        else if (jsonMsg['content'] == "-") {
            currentVal -= 1;
        }
        $("#"+jsonMsg['msrc'] + "-model").html(currentVal.toString());
        

        //处理默认选择
        updateWorkerStatus();
        updateModelWorkerStatus();
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
        $("#ws-build-log").scrollTop(document.getElementById('ws-build-log').scrollHeight)
        $("#ws-build-log2").append(jsonMsg['content']);
        $("#ws-build-log2").append('<br>');
        $("#ws-build-log2").scrollTop(document.getElementById('ws-build-log2').scrollHeight)
    }
    //更新进度
    else if (jsonMsg['msrc'] == 'ws-build-progress') {
        $("#ws-build-progress").attr("style","width:"+jsonMsg['content']+"%;");
        $("#ws-build-progress-text").text(jsonMsg['content']+"%");
    }
    //打包完成
    else if (jsonMsg['msrc'] == 'ws-build-finish') {
        $("#ws-build-log").append('<p>');
        $("#ws-build-log").append("<font color='green'>------------------------------------------------------------------------------------------------------------</font>");
        $("#ws-build-log").append('<p>');
        $("#ws-build-log").append("<font color='green'><h4>打包完成!!</h4></font>");
        $("#ws-build-log").append('<p>');
        $("#ws-build-log").scrollTop(document.getElementById('ws-build-log').scrollHeight)
        $("#ws-build-log2").append('<p>');
        $("#ws-build-log2").append("<font color='green'>------------------------------------------------------------------------------------------------------------</font>");
        $("#ws-build-log2").append('<p>');
        $("#ws-build-log2").append("<font color='green'><h4>打包完成!!</h4></font>");
        $("#ws-build-log2").append('<p>');
        $("#ws-build-log2").scrollTop(document.getElementById('ws-build-log2').scrollHeight)
    }
    //关注的编译机开始工作
    else if (jsonMsg['msrc'] == 'ws-build-reset') {
        $("#ws-build-log").empty();
        $("#ws-build-log2").empty();
        $("#ws-build-progress").attr("style","width:0%;");
        $("#ws-build-progress-text").text("0%");
    }
    else if (jsonMsg['msrc'] == 'ws-crx-update') {
        $("#updateModal").modal();
    }
    //更新使用者信息
    else if (jsonMsg['msrc'] == 'ws-user-info') {
        ctx = jsonMsg['content'].split('|');
        info = String.format("当前用户：{0} ; 打包原因：{1}",ctx[0],ctx[1]);
        content = String.format('<a href=\"#\" rel=\"tooltip\" title=\"{0}\"><font color=\"black\">{1}</font></a>',info,info);
        $("#ws-user-info").empty();
        $("#ws-user-info").append(content);
    }
    //更新默认版本号
    else if (jsonMsg['msrc'] == 'ws-installer-version') {
        ctx = jsonMsg['content'].split('.');
        $("#ws-build-v1").val(ctx[0]);
        $("#ws-build-v2").val(ctx[1]);
        $("#ws-build-v3").val(ctx[2]);
        $("#ws-build-v4").val(ctx[3]);
    }
    //更新默认supplyid
    else if (jsonMsg['msrc'] == 'ws-installer-supplyid') {
        $("#ws-installer-supplyid").val(jsonMsg['content']);
    }
    //更新默认版本标记细节
    else if (jsonMsg['msrc'] == 'ws-markup-detail') {
        $("#ws-markup-detail").val(jsonMsg['content']);
    }
    //更新默认打包原因
    else if (jsonMsg['msrc'] == 'ws-build-reason') {
        $("#ws-build-reason").val(jsonMsg['content']);
    }
    //更新默认使用者email
    else if (jsonMsg['msrc'] == 'ws-user-email') {
        $("#ws-user-email").val(jsonMsg['content']);
    }
    //更新版本构造细节
    else if (jsonMsg['msrc'] == 'ws-cb-detail') {
        $("#ws-cb-detail").val(jsonMsg['content']);
    }
    //更新归档目录
    else if (jsonMsg['msrc'] == 'ws-installer-archive') {
        $("#ws-installer-archive").val(jsonMsg['content']);
    }
    //更新所有模版类别
    else if (jsonMsg['msrc'] == 'ws-model-category') {
        $("#ws-model-category").empty();
        var cates = jsonMsg['content'].split("|");
        $("#ws-model-category").append("<option class=\"default\" value=\"请选择编译模板的类别\">请选择编译模板的类别</option>");
        for (var index in cates) {
            var node = String.format("<option value=\"{0}\">{1}</option>",cates[index],cates[index]);
            $("#ws-model-category").append(node);
        }
    }
    //更新模板页的模板类别
    else if (jsonMsg['msrc'] == 'ws-update-category') {
        $("#ws-model-category-select").empty();
        $("#ws-model-name-select").empty();
        $("#ws-model-show-description").val("");
        $("#ws-model-show-remark").val("");

        var cates = jsonMsg['content'].split("|");
        $("#ws-model-category-select").append("<option class=\"default\" value=\"请选择编译模板的类别\">请选择编译模板的类别</option>");
        for (var index in cates) {
            var node = String.format("<option value=\"{0}\">{1}</option>",cates[index],cates[index]);
            $("#ws-model-category-select").append(node);
        }
    }
    //更新某模板类别下的模版
    else if (jsonMsg['msrc'] == 'ws-category-select') {
        $("#ws-model-name-select").empty();
        var models = jsonMsg['content'].split("|");
        for (var index in models) {
            var info = models[index].split(';');
            var node = String.format("<option product=\"{0}\" value=\"{1}\">{2}</option>",info[0],info[1],info[1]);
            $("#ws-model-name-select").append(node);
        }
        $("#ws-model-name-select").change();
    }
    //更新模板功能说明和注意事项
    else if (jsonMsg['msrc'] == 'ws-model-select') {
        var infos = jsonMsg['content'].split("|");
        var reg=new RegExp("<br>","g");
        $("#ws-model-show-description").val(infos[0].replace(reg,"\n"));
        $("#ws-model-show-remark").val(infos[1].replace(reg,"\n"));
    }
    //activate模板化实例
    else if (jsonMsg['msrc'] == 'ws-model-activate') {
        //将模板内容应用到Build页
        var ctx = jsonMsg['content'].split('|');
        var worker = ctx[0];
        var product = ctx[1];
        var slns = ctx[2];
        var build_options = ctx[3];
        var markupcode = ctx[4];
        var markupdetail = ctx[5];
        var prefix = ctx[6];
        var v1 = ctx[7];
        var v2 = ctx[8];
        var v3 = ctx[9];
        var v4 = ctx[10];
        var postfix = ctx[11];
        var archive = ctx[12];
        var reason = ctx[13];
        var email = ctx[14];
        var supplyid = ctx[15];
        var codebase = ctx[16];
        var cbdetail = ctx[17];

        //应用解决方案配置
        var items = slns.split(";");
        for (var i in items) {
            var item = items[i];
            var info = item.split(",");
            $(".btn[id^='ws-btn-slnselect-']").each( function() {
                if ($(this).children().html() == info[0]) {
                    if(($(this).hasClass("active") && info[1] == '0') || (!$(this).hasClass("active") && info[1] == '1')) {
                        $(this).click();
                    }
                }
            })
        }
        //应用打包选项
        items = build_options.split(";");
        for (var i in items) {
            var item = items[i];
            var info = item.split(",");
            $(".btn[id^='ws-btn-option-']").each( function() {
                if ($(this).children().attr("name") == info[0]) {
                    if($(this).parent().hasClass("btn-group")) {
                        if ($(this).children().attr("value") == info[1]) {
                            $(this).click();
                        }
                    }
                    else {
                        if(($(this).hasClass("active") && info[1] == '0') || (!$(this).hasClass("active") && info[1] == '1')) {
                            $(this).click();
                        }
                    }
                }
            })   
        }
        //应用额外选项
        items = prefix.split(",");
        $("#ws-build-prefix").val(items[1]);
        items = v1.split(",");
        $("#ws-build-v1").val(items[1]);
        items = v2.split(",");
        $("#ws-build-v2").val(items[1]);
        items = v3.split(",");
        $("#ws-build-v3").val(items[1]);
        items = v4.split(",");
        $("#ws-build-v4").val(items[1]);
        items = postfix.split(",");
        $("#ws-build-postfix").val(items[1]);
        items = archive.split(",");
        $("#ws-installer-archive").val(items[1]);
        items = reason.split(",");
        $("#ws-build-reason").val(items[1]);
        items = email.split(",");
        $("#ws-user-email").val(items[1]);
        items = supplyid.substr(9);
        $("#ws-installer-supplyid").val(items);
        items = markupcode.split(",");
        $(".btn[id^='ws-btn-markup-code-']").each( function() {
            if ($(this).attr("value") == items[1]) {
                $(this).click();
            }
        })
        items = markupdetail.split(",");
        $("#ws-markup-detail").val(items[1]);
        items = codebase.split(",");
        $(".btn[id^='ws-btn-codebase-']").each( function() {
            if ($(this).attr("value") == items[1]) {
                $(this).click();
            }
        })
        items = cbdetail.split(",");
        $("#ws-cb-detail").val(items[1]);

        //应用worker
        var nickname = $("#"+worker).html();
        $("#ws-worker-select").val(nickname);

        //切换到Build页

        $(".nav-pills").children().removeClass("active");
        $(".tab-content").children().removeClass("active");
        $("#tabMain-title").addClass("active");
        $("#tabMain").addClass("active");
        initUI();
        
        //alert(jsonMsg['content']);
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

//default build按钮默认行为
function onDefaultBuildBtnClick() {
    $(".btn[id^='ws-btn-slnselect-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                $(this).click();
            }
        }
        else {
            if ($(this).attr('default') == 'true') {
                $(this).click();
            }
        }
    })
}

//default options按钮响应
function onDefaultOptionsBtnClick() {
    $(".btn[id^='ws-btn-option-']").each( function() {
        if ($(this).hasClass("active")) {
            if ($(this).attr('default') != 'true') {
                $(this).click();
            }
        }
        else {
            if ($(this).attr('default') == 'true') {
                $(this).click();
            }
        }
    })
}

//点击更换项目
function onProjectSelect() {
    //清空sln项目和build-options
    $("#ws-sln-select-base").empty();
    $("#ws-sln-select-base").append("<span class=\"label label-success\">公共类库</span>&nbsp;");
    $("#ws-sln-select-middle").empty();
    $("#ws-sln-select-middle").append("<span class=\"label label-success\">公共组件</span>&nbsp;");
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
    //清空markup-code
    $("#ws-markup-code").empty();

    var currentSel = $("#ws-project-select option:selected").text();
    var msg = formatMessage("ws-sln-select",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-build-options",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-code-base",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-markup-code",currentSel);
    worker.postMessage(msg);
}

function updateWorkerStatus(bNotify) {
    $("#ws-worker-status").removeClass();
    $("#ws-worker-detail").removeClass();

    var cls = $("#ws-worker-select option:selected").attr('class');
    var ip = $("#ws-worker-select option:selected").attr('ip');
    
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
        if (bNotify) {
            var currentSel = $("#ws-worker-select option:selected").attr('id');
            msg = formatMessage("ws-worker-select",currentSel);
            worker.postMessage(msg);
            msg = formatMessage("ws-query-buildlog","");
            worker.postMessage(msg);
        }
    }
}

function updateModelWorkerStatus() {
    $("#ws-model-worker-status").removeClass();
    $("#ws-model-worker-detail").removeClass();

    var cls = $("#ws-model-worker-select option:selected").attr('class');
    var ip = $("#ws-model-worker-select option:selected").attr('ip');
    
    if (cls == undefined || ip == undefined) {
        $("#ws-model-worker-status").text("None");
        $("#ws-model-worker-status").addClass("label label-warning");
        $("#ws-model-worker-detail").addClass("label label-warning");
        $("#ws-model-worker-detail").text("目前没有在线的编译机");
    }
    else {
        $("#ws-model-worker-status").text(ip);
        if (cls == "running") {
            $("#ws-model-worker-status").addClass("label label-success");
            $("#ws-model-worker-detail").addClass("label label-success");
            $("#ws-model-worker-detail").text("系统当前正在打包，请稍等...");
        }
        else if (cls == "idle") {
            $("#ws-model-worker-status").addClass("label");
            $("#ws-model-worker-detail").addClass("label label");
            $("#ws-model-worker-detail").text("该编译机当前空闲");
        }
        else if (cls == "error") {
            $("#ws-model-worker-status").addClass("label label-important");
            $("#ws-model-worker-detail").addClass("label label-important");
            $("#ws-model-worker-detail").text("该编译机出现错误");
        }
    }
}

//切换worker响应
function onWorkerSelect() {
    //清空日志输出区域
    $("#ws-build-log").empty();
    $("#ws-build-log2").empty();

    updateWorkerStatus(true);
}

//切换model worker响应
function onModelWorkerSelect() {
    updateModelWorkerStatus();
}

//切换model category
function onModelCategorySelect() {
    if ($("#ws-model-category-select option:selected").hasClass("default")) {
        $("#ws-model-name-select").empty();
        $("#ws-model-show-description").val("");
        $("#ws-model-show-remark").val("");
        return;
    }
    var modelCategory = $("#ws-model-category-select option:selected").text();
    var msg = formatMessage("ws-category-select",modelCategory);
    worker.postMessage(msg);
}

//切换model name
function onModelNameSelect () {
    var modelCategory = $("#ws-model-category-select option:selected").text();
    var modelName = $("#ws-model-name-select option:selected").text();
    var info = String.format("{0}|{1}",modelCategory,modelName);
    var msg = formatMessage("ws-model-select",info);
    worker.postMessage(msg);
    var projName = $("#ws-model-name-select option:selected").attr("product");
    $("#ws-project-select").val(projName);
    $("#ws-project-select").change();
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

function onBtnProjectSwitchClick() {
    $(".btn[id^='ws-btn-slnselect-']").each( function() {
        $(this).click();
    })
}

function onBtnOptionsSwitchClick() {

    $(".btn[id^='ws-btn-option-']").each( function() {
        if ($(this).children().attr('value') == undefined) {
            $(this).click();
        }
    })
    $("div[id^='ws-btn-option-']").each( function() {
        if ($(this).attr("data-toggle") == 'buttons-radio') {
            nodeDefault = null;
            node0 = null;
            var allNodes = $(this).children();
            for (var i = 0; i < allNodes.length; i++) {
                if (allNodes[i].attributes['default'] != undefined) {
                    if (allNodes[i].attributes['default'].nodeValue == 'true') {
                        nodeDefault = allNodes[i];
                    }
                }
                var innerNode = allNodes[i].innerHTML;
                if (innerNode.indexOf("value=\"0\"") != -1) {
                    node0 = allNodes[i];
                }
            }
            if (nodeDefault != null && node0 != null) {
                bDefaultActive = false;
                for (var i = 0; i < nodeDefault.classList.length; i++) {
                    if (nodeDefault.classList[i] == 'active') {
                        bDefaultActive = true;
                    }
                };
                if (bDefaultActive) {
                    node0.click();
                }
                else {
                    nodeDefault.click();
                }
            }
        }
    })
}
