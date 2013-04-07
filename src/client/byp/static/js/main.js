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

    //更改tooltip颜色
    //$('a.tooltip-colorfy').hover(function() {changeTooltipColorTo('#f00')});
}

$(document).ready(function() {
    //初始化UI
    initUI();

    //start backend communication worker
    worker = new Worker("static/js/worker.js");
    worker.onmessage = function(evt) {
        updateUI(evt.data)
    };
    
});


function updateUI(msg) {
    $("#ws-build-log").append(msg);
    $("#ws-build-log").append('<br>');

    var jsonMsg = JSON.parse(msg)
    if (jsonMsg['msrc'] == "ws-project-select") {
        //清空project项目
        $("#ws-project-select").empty();

        var projs = jsonMsg['content'].split(",");
        for (var index in projs) {
            var node = String.format("<option value=\"{0}\">{1}</option>",projs[index],projs[index]);
            $("#ws-project-select").append(node);
        }
    }
    else if (jsonMsg['msrc'] == "ws-sln-select") {
        var sln = jsonMsg['content'].split(",");
        var slnName = sln[0];
        var slnTooltip = String.format("{0},责任人:{1}",sln[1],sln[2]);
        var btnId = "ws-btn-slnselect-" + randomChar(32);
        var node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\">{2}</a></button>",btnId,slnTooltip,slnName);
        $("#ws-sln-select").append(node);
        $("#"+btnId).bind('click',onInverseBtnClick);
    }
    else if (jsonMsg['msrc'] == 'ws-build-options') {
        var ctx = jsonMsg['content'].split("|");
        if (ctx[1] == 'check') {
            var info = ctx[2].split(",");
            var btnId = "ws-btn-option-" + randomChar(32);
            var node = String.format("<button type=\"button\" id=\"{0}\" class=\"btn btn-mini\" class-toggle=\"btn-inverse\" data-toggle=\"button\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\">{2}</a></button>",btnId,info[1],info[0]);
            $("#ws-build-options").append(node);
            $("#"+btnId).bind('click',onInverseBtnClick);
        }
        else if (ctx[1] == 'radio') {
            var arr = new Array();
            var btnId = "ws-btn-option-" + randomChar(32);
            var node = String.format("<div id=\"{0}\" class=\"btn-group\" data-toggle=\"buttons-radio\">",btnId);
            arr.push(btnId);
            var info = ctx[2].split(";");
            for (var index in info) {
                var items = info[index].split(",");
                var btnId = "ws-btn-option-" + randomChar(32);
                var option = String.format("<button type=\"button\" id=\"{0}\" class-toggle=\"btn-inverse\" class=\"btn btn-mini\"><a href=\"#\" rel=\"tooltip\" title=\"{1}\" value=\"{2}\">{3}</a></button>",btnId,items[1],items[2],items[0]);
                node += option;
                arr.push(btnId);
            }
            node += "</div>"
            $("#ws-build-options").append(node);
            for (var index in arr) {
                $("#"+arr[index]).bind('click',onInverseBtnClick);
            }
        }
    }
    else if (jsonMsg['msrc'] == 'ws-code-base') {
        alert("ws-code-base");
    }


    //重新初始化UI
    initUI();
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


$('.btn-group > .btn, .btn[data-toggle="button"]').click(onInverseBtnClick);


$('#ws-project-select').change(function() {
    //清除ws-sln-select 和ws-build-options 下所有bind
    //
    //清空sln项目
    $("#ws-sln-select").empty();
    $("#ws-build-options").empty();

    var currentSel = document.getElementById("ws-project-select").value
    var msg = formatMessage("ws-sln-select",currentSel);
    worker.postMessage(msg);
    msg = formatMessage("ws-build-options",currentSel);
    worker.postMessage(msg);
});

$('#ws-worker-select').change(function() {
    alert('ws-worker-select changed.');
});

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
