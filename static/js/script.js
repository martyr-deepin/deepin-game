jQuery(function(){
  /**
  some settings
  **/

  var ENTER_KEY = 13;
  var ESC_KEY = 27;
  var jQuerycontainer = jQuery('.game_gallery');
  if(jQuerycontainer.masonry)jQuerycontainer.masonry({
    itemSelector: '.box',
    columnWidth: 119
  });
  jQuery(".game_pic").mouseenter(function(){
  var jQuerygame_action = jQuery(this).children(".game_action")
			jQuerygame_action.css("left", (jQuery(this).width()-jQuerygame_action.width())/2);
  });
  jQuery(".summary > .brief_intro").each(function(i,v){
  	if(jQuery(v).height() > parseInt(jQuery(v).css("font-size"))*2){
  	  jQuery(v).height(parseInt(jQuery(v).css("font-size"))*2+5);
  	  jQuery(v).after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>');
  	}
  });
  jQuery(".summary > .brief_intro").parent().click(function(e){
  	switch(e.target.hash){
  		case "#expand":
  		e.preventDefault();
  		jQuery(e.target).siblings(".brief_intro").height("");
  		jQuery(e.target).siblings(".brief_intro").after('<a href="#collapse" style="float:right; padding:5px 0 0; color:#0d6bc2;">&nbsp;收起&nbsp;&uarr;</a>');
  		jQuery(e.target).remove();
  		break;
  		case "#collapse":
  		e.preventDefault();
  		jQuery(e.target).siblings(".brief_intro").height(parseInt(jQuery(e.target).siblings(".brief_intro").css("font-size"))*2+5);
  		jQuery(e.target).siblings(".brief_intro").after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&nbsp;展开&nbsp;&darr;</a>')
  		jQuery(e.target).remove();
  		default:
  		break;
  	}
  });
  jQuery(".text_box > .brief_intro, .text_box > .guide").each(function(i,v){
  	if(jQuery(v).height() > parseInt(jQuery(v).css("font-size"))*5){
  	  jQuery(v).height(parseInt(jQuery(v).css("font-size"))*5+12.5);
  	  jQuery(v).after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>');
  	}
  });
  jQuery(".text_box > .brief_intro,.text_box > .guide").parent().click(function(e){
  	switch(e.target.hash){
  		case "#expand":
  		e.preventDefault();
  		jQuery(e.target).siblings().height("");
  		jQuery(e.target).siblings().after('<a href="#collapse" style="float:right; padding:5px 0 0; color:#0d6bc2;">&minus;&nbsp;收起</a>');
  		jQuery(e.target).remove();
  		break;
  		case "#collapse":
  		e.preventDefault();
  		jQuery(e.target).siblings().height(parseInt(jQuery(e.target).siblings().css("font-size"))*5+12.5);
  		jQuery(e.target).siblings().after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>')
  		jQuery(e.target).remove();
  		default:
  		break;
  	}
  });

  var search_text, search_btn;
  search_text = jQuery("#search_text");
  search_btn  = jQuery("#search_botton");
  search_text.keydown(function(e){
    if(e.keyCode == ENTER_KEY){
        search_btn.click();
        $('#ui_element').find('.sb_dropdown').hide();
    }
    else if (e.keyCode == ESC_KEY){
        $('#ui_element').find('.sb_dropdown').slideUp('fast');
    }
    else{
        $('#ui_element').find('.sb_dropdown').slideDown('fast');
    }
  });

  search_btn.click(function(){
    if (search_text.val() != ''){
        jQuery("#game-gallery")[0].src = 'http://game-center.linuxdeepin.com/game/search/?q=' + search_text.val();
    }
  });
  
});

function change_color_theme(name){
    var old_color = $("#color_link");
    if (old_color){
        var old_color_link = old_color.attr("href");
        new_color_link = old_color_link.split('_')[0] +"_" + name + '.css';
        $("#color_link").attr("href", new_color_link);
        $.cookie('color', name, {"expires": 365 * 20, 'path': '/'});
    }
}

$(document).ready(function(){
    var theme_color = $.cookie('color');
    if (theme_color){
        change_color_theme(theme_color);
    }
});

// search popup
$(function() {
    var $ui = $('#ui_element');
    //$ui.find('.sb_input').bind('focus',function(e){
        //console.log(e.keyCode);
        //$ui.find('.sb_dropdown').slideDown('fast');
    //});

    $ui.find('.sb_input').bind('click',function(e){
        $ui.find('.sb_dropdown').slideDown('fast');
    });

    $ui.bind('blur',function(){
        $ui.find('.sb_dropdown').slideUp('fast');
    });

    $ui.bind('mouseleave',function(){
        $ui.find('.sb_dropdown').slideUp('fast');
    });
    
    $ui.find('.sb_dropdown').bind('mouseleave',function(){
        $ui.find('.sb_dropdown').slideUp('fast');
    });

    $ui.find('.sb_dropdown').bind('click',function(){
        $ui.find('.sb_dropdown').hide();
    });

});
