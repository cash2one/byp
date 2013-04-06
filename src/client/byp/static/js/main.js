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

$(document).ready(function() {
    //初始化combobox
    $('.combobox').combobox();

	//初始化tooltip功能
    $(function () {
        $("[rel='tooltip']").tooltip();
    });

    //start backend communication worker
    worker = new Worker("static/js/worker.js");
    worker.onmessage = function(evt) {
        $("#ws-build-log").append(evt.data);
        $("#ws-build-log").append('<br>');
    };
    
});

//checkbox color change action
$('.btn-group > .btn, .btn[data-toggle="button"]').click(function() {

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
      
});

$('#ws-project-select').change(function() {
    worker.postMessage("ws-project-select");
});

$('#ws-worker-select').change(function() {
    alert('ws-worker-select changed.');
});

