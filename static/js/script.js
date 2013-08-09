$(function(){
  var $container = $('.game_gallery');
  if($container.masonry)$container.masonry({
    itemSelector: '.box',
    columnWidth: 119
  });
  $(".game_pic").mouseenter(function(){
  var $game_action = $(this).children(".game_action")
			$game_action.css("left", ($(this).width()-$game_action.width())/2);
  });
  $(".summary > .brief_intro").each(function(i,v){
  	if($(v).height() > parseInt($(v).css("font-size"))*2){
  	  $(v).height(parseInt($(v).css("font-size"))*2+5);
  	  $(v).after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>');
  	}
  });
  $(".summary > .brief_intro").parent().click(function(e){
  	switch(e.target.hash){
  		case "#expand":
  		e.preventDefault();
  		$(e.target).siblings(".brief_intro").height("");
  		$(e.target).siblings(".brief_intro").after('<a href="#collapse" style="float:right; padding:5px 0 0; color:#0d6bc2;">&minus;&nbsp;收起</a>');
  		$(e.target).remove();
  		break;
  		case "#collapse":
  		e.preventDefault();
  		$(e.target).siblings(".brief_intro").height(parseInt($(e.target).siblings(".brief_intro").css("font-size"))*2+5);
  		$(e.target).siblings(".brief_intro").after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>')
  		$(e.target).remove();
  		default:
  		break;
  	}
  });
  $(".text_box > .brief_intro, .text_box > .guide").each(function(i,v){
  	if($(v).height() > parseInt($(v).css("font-size"))*5){
  	  $(v).height(parseInt($(v).css("font-size"))*5+12.5);
  	  $(v).after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>');
  	}
  });
  $(".text_box > .brief_intro,.text_box > .guide").parent().click(function(e){
  	switch(e.target.hash){
  		case "#expand":
  		e.preventDefault();
  		$(e.target).siblings().height("");
  		$(e.target).siblings().after('<a href="#collapse" style="float:right; padding:5px 0 0; color:#0d6bc2;">&minus;&nbsp;收起</a>');
  		$(e.target).remove();
  		break;
  		case "#collapse":
  		e.preventDefault();
  		$(e.target).siblings().height(parseInt($(e.target).siblings().css("font-size"))*5+12.5);
  		$(e.target).siblings().after('<a href="#expand" style="float:right; padding:5px 0 0; color:#0d6bc2;">&plus;&nbsp;展开</a>')
  		$(e.target).remove();
  		default:
  		break;
  	}
  });
});