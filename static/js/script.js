jQuery(function(){
  /**
  some settings
  **/
  var debug = true;
  var server_address;
  if (debug){
    server_address = 'http://59.173.241.82:11111/';
  }
  else{
    server_address = 'http://game-center.linuxdeepin.com/';
  }

  var ENTER_KEY = 13;
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
  var search_text, search_btn, search_msg;
  search_text = jQuery(".search_box .text");
  search_btn  = jQuery(".search_box .search");
  search_msg  = jQuery('<div class="search_msg" />');
  search_text.keydown(function(e){
    if(e.keyCode == ENTER_KEY){
      search_btn.click();
    }
  });
  search_btn.click(function(){
    jQuery("#game-gallery")[0].src = server_address + 'game/search/?q=' + search_text.val();
    search_msg.text( '"' + search_text.val() + '"' + " 的搜索结果");
    jQuery(".nav_bar .tabs").replaceWith(search_msg);
  });
});