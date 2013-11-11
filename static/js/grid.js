
	/**
	 * VARIABLES
	 *
	 * Global variables used within functions and event handlers.
	 */
	var animate_speed=300,easing_method='easeOutExpo';
	var contact_height=null,login_height=null;
	var debug=false;
	
	/**
	 * GRID SETUP
	 *
	 * Setup initial grid display and page actions.
	 */
	$(function() {
		setup_grid();
		setup_dropdowns();
		setup_contact();
	});

	/**
	 * ISSET
	 *
	 * PHP style isset() method for variables and objects.
	 *
	 * @param mixed variables.
	 */
	function isset(variable)  {
		try {
			if(typeof(eval(variable))!='undefined')
			if(eval(variable)!=null) return true;
		} catch(e) {}
		return false;
	}
	
	/**
	 * TRACE
	 *
	 * Browser safe console logging method.
	 *
	 * @param string msg
	 */
	function trace(msg) {
		try {window.console.log(msg)} catch (err) {}
	}
	
	/**
	 * SLIDER_UPDATE
	 *
	 * Logo block slider event handler.
	 */
	function slider_update(e) {
	
		var values=get_slider_values();
		
		//
		// Calculate Difference
		var diff=Math.floor((150-(values.work+values.company+values.now))/2);
		if(debug) trace('slider adjustment: '+diff);
		
		//
		// Adjust Sliders
		switch($(e.target).parents('.group').find('span:first').text()) {
		
			case 'work':
				$('header.top .logo .group:eq(1) .slider').slider('value',(values.company+diff));
				$('header.top .logo .group:eq(2) .slider').slider('value',(values.now+diff));
				break;
			
			case 'company':
				$('header.top .logo .group:eq(0) .slider').slider('value',(values.work+diff));
				$('header.top .logo .group:eq(2) .slider').slider('value',(values.now+diff));
				break;
			
			case 'now':
				$('header.top .logo .group:eq(0) .slider').slider('value',(values.work+diff));
				$('header.top .logo .group:eq(1) .slider').slider('value',(values.company+diff));
				break;
		
		}
		
	}
	
	/**
	 * GET_SLIDER_VALUES
	 *
	 * Retrieve values from logo block sliders.
	 */
	function get_slider_values() {
		var values={
			work: Math.floor($('header.top .logo .group:eq(0) .slider').slider('value')),
			company: Math.floor($('header.top .logo .group:eq(1) .slider').slider('value')),
			now: Math.floor($('header.top .logo .group:eq(2) .slider').slider('value'))
		};
		if(isNaN(values.work)) values.work = 50;
		if(isNaN(values.company)) values.company = 50;
		if(isNaN(values.now)) values.now = 50;
		return values;
	}
	
	/**
	 * SETUP_DROPDOWNS
	 *
	 * Setup contact and login dropdown elements.
	 */
	function setup_dropdowns() {
		
		contact_height=$('header.top div.contact').height();
		login_height=$('header.top div.login').height();
		
		$('header.top nav li.contact a').click(function() {
			if($('header.top div.contact').is(':hidden')) {
				$(this).addClass('active');
				$('header.top .logo').css({zIndex:10});
				$('header.top div.contact').css({display:'block',height:0}).stop().animate({height:contact_height+'px'},animate_speed,easing_method);
			} else {
				$(this).removeClass('active');
				$('header.top div.contact').stop().animate({height:0},animate_speed,easing_method,function() { $(this).hide(); $('header.top .logo').css({zIndex:55}); });
			}
			return false;
		});
		
		$('header.top nav li.login a').click(function() {
			if($('header.top div.login').is(':hidden')) {
				$(this).addClass('active');
				$('header.top div.login').css({display:'block',height:0}).stop().animate({height:login_height+'px'},animate_speed,easing_method);
			} else {
				$(this).removeClass('active');
				$('header.top div.login').stop().animate({height:0},animate_speed,easing_method,function() { $(this).hide(); });
			}
			return false;
		});
		
		$('header.top div.login form a.submit').click(function() {
			$(this).parents('form').submit();
			return false;
		});
		
	}
	
	/**
	 * SETUP_CONTACT
	 *
	 * Setup and handle contact form.
	 */
	function setup_contact() {
	
		$('#contact-form a.submit').click(function() {
		
			var form = $(this).parents('form');
			var name = $(form).find("input[name='name']").val();
			var email = $(form).find("input[name='email']").val();
			var location = $(form).find("input[name='location']").val();
			var whyus = $(form).find("input[name='whyus']").val();
			var message = $(form).find("textarea[name='message']").val();
			var formkey = $(form).find("input[name='formkey']").val();
			
			$.ajax({
				type: "POST",
				url: "/contact/post",
				data: {
					name: name,
					email: email,
					location: location,
					whyus: whyus,
					message: message,
					formkey: formkey
				},
				success: function(data) {
					
					clear_errors(form);
					
					if(data.result=='failed') {
						
						//
						// Set Error Fields
						for(key in data.errors) {
							if($("input[name='"+key+"']:visible").length>0)
								set_error($("input[name='"+key+"']:visible"));
							else if($("textarea[name='"+key+"']:visible").length>0)
								set_error($("textarea[name='"+key+"']:visible"));
						}
					
					} else if(data.result=='success') {
						
						clear_form(form);
						
					}
					
				},
				dataType: 'json'
			});
			
			return false;
		
		});
		
	}
	
	// --------------------------------------------- GRID METHODS ------------------------------------------------- //
	
	var grid=null,rows=200,columns=4,max_rows=200,max_items=200;
	var row_height=176,column_width=242;
	var strict=false,overlay=false,building=false,scroll=false,filter=false;
	var grid_full=false,loading_items=false;
	
	/**
	 * SETUP_GRID
	 *
	 * Setup grid and apply event handlers.
	 */
	function setup_grid() {
		
		// grid setup
		set_columns();
		$(window).resize(function() { if(columns!=set_columns()) place_grid_items(true); });
		$('#grid .item').hide();
		
		// scroll loader
		if(scroll) $(window).bind('scroll',scroll_handler);
		
		// item actions
		item_actions();
		
		// place items
		place_grid_items(false);
		
		// check height
		if(scroll) scroll_handler(null);
	
	}
	
	/**
	 * ITEM_ACTIONS
	 *
	 * Apply event handlers to individual grid elements.
	 */
	function item_actions() {
		
		//
		// Caption Element Popup
		$('#grid div.caption:hidden').hover(function() {},function() {
			if(!building) {
				//fadein_grid(this);
				//$(this).find('.popup').stop().animate({bottom:'-87px'},Math.floor(animate_speed/2),easing_method);
				//$(this).find('span.icon').css({zIndex:60});
			}
		});
		$('#grid .caption:hidden span.icon').hover(function() {
			if(!building) {
				//fadeout_grid($(this).parents('.item'));
				//$(this).parents('.item').find('.popup').stop().animate({bottom:0},animate_speed,easing_method);
				//$(this).css({zIndex:40});
			}
		},function() {});
		
		//
		// Blog Element Popup
		$('#grid div.blog:hidden').hover(function() {},function() {
			if(!building) {
				fadein_grid(this);
				$(this).find('.popup').stop().animate({bottom:'-40px'},Math.floor(animate_speed/2),easing_method);
				$(this).find('span.icon').css({zIndex:60});
			}
		});
		$('#grid .blog:hidden span.icon').hover(function() {
			if(!building) {
				fadeout_grid($(this).parents('.item'));
				$(this).parents('.item').find('.popup').stop().animate({bottom:0},animate_speed,easing_method);
				$(this).css({zIndex:40});
			}
		},function() {});
		
		//
		// Blog Viewer
		$('#grid .blog:hidden a.over').click(function() {
		
			var item = $(this).parents('.item');
			building = true;
			
			//
			// Apply Styles
			$(item).addClass('blogopen');
			$('#grid').css({zIndex: 500});
			fadeout_grid(item);
			
			//
			// Show / Hide Blog Elements
			$(item).find('a.over').hide();
			$(item).find('span.icon').hide();
			$(item).find('.popup').stop().css({bottom:'-40px'}).hide();
			$(item).find('a.close').show();
			
			//
			// Set Up Scrollbar
			$(item).find('div.scrollbar').slider({
				orientation: "vertical",
				min: 0,
				max: 570,
				value: 570,
				change: scroll_handler,
				slide: scroll_handler
			});
			
			//
			// Scroll Handler
			function scroll_handler( event, ui ) {
				var percentage = (570-ui.value)/570;
				var body_height = $(item).find('div.body').height();
				var position = -((body_height-630)*percentage);
				$(item).find('div.body').css({top: position+'px'});
			}
			
			//
			// Capture Mousewheel
			$(item).find('div.scrolling').mousewheel(function(event, delta) {
				var dir = delta > 0 ? 'up' : 'down';
				var scrollbar = $(event.target).parents('.item').find('div.scrollbar');
				var value = $(scrollbar).slider("value");
				if(dir=='up') {
					value += 15;
					$(scrollbar).slider("value", value);
				} else {
					value -= 15;
					$(scrollbar).slider("value", value);
				}
				return false;
			});
			
			//
			// Get Sizes
			var grid_width = $('#grid').width()-6;
			var item_left = parseInt($(item).css('left'));
			var grid_height = $('#grid').height()-6;
			var item_top = parseInt($(item).css('top'));
			var adjust_left = item_left;
			var adjust_top = item_top;
			
			//
			// Adjust Left Position
			$(item).data('return_left',item_left);
			$(item).data('slideout_return_left',item_left);
			if((item_left+620)>grid_width) {
				adjust_left = item_left - ((item_left+620)-grid_width);
			}
			
			//
			// Adjust Top Position
			$(item).data('return_top',item_top);
			if((item_top+818)>grid_height) {
				adjust_top = item_top - ((item_top+818)-grid_height);
			}
		
			//
			// Expand Blog
			$(item).css({zIndex:2000}).animate({width:'620px', height:'818px', left:adjust_left+'px', top:adjust_top+'px'}, animate_speed/2, function() {
				$(this).find('a.twitter').fadeIn(100);
				$(this).find('a.facebook').fadeIn(100);
				$(this).find('a.comments').fadeIn(100);
				$(this).find('div.scrolling').fadeIn(100);
				$(this).find('div.scrollbar').fadeIn(100);
			});
			
			return false;
			
		});
		
		//
		// Close Blog Viewer
		$('#grid .blog:hidden a.close').click(function() {
			
			var item = $(this).parents('.item');
			
			//
			// Remove Styles
			$(item).removeClass('blogopen');
			$('#grid').css({zIndex: 10});
			
			//
			// Show / Hide Blog Elements
			$(item).find('a.over').show();
			$(item).find('span.icon').show();
			$(item).find('.popup').show();
			$(item).find('a.close').hide();
			$(item).find('a.twitter').hide();
			$(item).find('a.facebook').hide();
			$(item).find('a.comments').hide();
			$(item).find('div.scrolling').hide();
			$(item).find('div.scrollbar').hide();
			
			//
			// Contract Blog
			contract_twitter(item, true);
			contract_comments(item, true);
			$(item).css({overflow: 'hidden'}).animate({width:'250px', height:'180px', left:$(item).data('return_left')+'px', top:$(item).data('return_top')+'px'}, animate_speed/2, function() {
				building = false;
				fadein_grid(item);
			});
			
			return false;
			
		});
		
		//
		// Blog Expand Twitter
		$('#grid .blog:hidden a.twitter').click(function() {
		
			var item = $(this).parents('.item');
			contract_comments(item, false);
			if($(item).find('div.twitter').is(':hidden')) {
			
				//
				// Check Right Tolerance
				var grid_width = $('#grid').width()-6;
				var item_left = parseInt($(item).css('left'));
				var adjust_left = item_left;
			
				//
				// Adjust Left Position
				$(item).data('slideout_return_left',item_left);
				if((item_left+620+320)>grid_width) {
					adjust_left = item_left - ((item_left+620+320)-grid_width);
				}
			
				//
				// Do Slideout
				$(this).addClass('twitter_active');
				$(item).css({overflow:'visible'}).animate({left: adjust_left+'px'}, animate_speed/2).find('div.twitter').show().animate({right:'-320px'}, animate_speed/2);
			
			} else {
				contract_twitter(item, true);
			}
			
			return false;
			
		});
		
		//
		// Blog Contract Twitter
		function contract_twitter(item, overflow) {
			$(item).find('a.twitter').removeClass('twitter_active');
			$(item).animate({left: $(item).data('slideout_return_left')+'px'}, animate_speed/2).find('div.twitter').animate({right:0}, animate_speed/2, function() { $(this).hide(); if(overflow) $(item).css({overflow: 'hidden'}); });
		}
		
		//
		// Blog Expand Comments
		$('#grid .blog:hidden a.comments').click(function() {
		
			var item = $(this).parents('.item');
			contract_twitter(item, false);
			var comments = $(item).find('div.comments');
			if($(comments).is(':hidden')) {
			
				//
				// Check Height
				check_comments_height(comments);
			
				//
				// Check Right Tolerance
				var grid_width = $('#grid').width()-6;
				var item_left = parseInt($(item).css('left'));
				var adjust_left = item_left;
			
				//
				// Adjust Left Position
				$(item).data('slideout_return_left',item_left);
				if((item_left+620+320)>grid_width) {
					adjust_left = item_left - ((item_left+620+320)-grid_width);
				}
				
				//
				// Do Slideout
				$(this).addClass('comments_active');
				$(item).css({overflow:'visible'}).animate({left: adjust_left+'px'}, animate_speed/2).find('div.comments').show().animate({right:'-320px'}, animate_speed/2);
				
			} else {
				contract_comments(item, true);
			}
			
			return false;
			
		});
		
		//
		// Blog Contract Comments
		function contract_comments(item, overflow) {
			$(item).find('a.comments').removeClass('comments_active');
			$(item).animate({left: $(item).data('slideout_return_left')+'px'}, animate_speed/2).find('div.comments').animate({right:0}, animate_speed/2, function() { $(this).hide(); if(overflow) $(item).css({overflow: 'hidden'}); });
		}
		
		//
		// Handle Comment Form
		$('#grid .blog:hidden form.commentform a.submit').click(function() {
		
			var form = $(this).parents('form');
			var name = $(form).find("input[name='name']").val();
			var email = $(form).find("input[name='email']").val();
			var website = $(form).find("input[name='website']").val();
			var comment = $(form).find("textarea[name='comment']").val();
			var uid = $(form).find("input[name='uid']").val();
			var formkey = $(form).find("input[name='formkey']").val();
			
			$.ajax({
				type: "POST",
				url: "/comments/post",
				data: {
					name: name,
					email: email,
					website: website,
					comment: comment,
					uid: uid,
					formkey: formkey
				},
				success: function(data) {
					
					clear_errors(form);
					
					if(data.result=='failed') {
						
						//
						// Set Error Fields
						for(key in data.errors) {
							if($("input[name='"+key+"']:visible").length>0)
								set_error($("input[name='"+key+"']:visible"));
							else if($("textarea[name='"+key+"']:visible").length>0)
								set_error($("textarea[name='"+key+"']:visible"));
						}
					
					} else if(data.result=='success') {
						
						clear_form(form);
						
						//
						// Add comment to ul
						$(form).parents('div.comments').find('ul').prepend(data.html);
						
						//
						// Update comment #
						var current = Math.floor($(form).parents('div.item').find('a.comments').text());
						if(current<=0||current==null||current==NaN) current=0;
						current++;
						$(form).parents('div.item').find('a.comments').text(current);
					
						//
						// Check height
						check_comments_height($(form).parents('div.comments'));
						
					}
					
				},
				dataType: 'json'
			});
			
			return false;
		
		});
		
		//
		// Handle Twitter Form
		$('#grid .blog:hidden form.twitterform a.submit').click(function() {
			var href = 'http://twitter.com/intent/tweet?';
			var form = $(this).parents('form');
			href += 'related='+encodeURIComponent($(form).find("input[name='related']").val());
			href += '&text='+encodeURIComponent($(form).find("textarea[name='text']").val());
			href += '&url='+encodeURIComponent($(form).find("input[name='url']").val());
			window.open(href, 'intent', 'scrollbars=yes,resizable=yes,toolbar=no,location=yes,width=550,height=420');
			return false;
		});
		
		//
		// Slider Element
		$('#grid .slider:hidden').each(function() {
		
			$(this).data('current',1);
			$(this).data('total',$(this).find('.slide').length);
			
			$(this).find('.slide').css({left:'-2000px',zIndex:1});
			$(this).find('.slide:first').css({left:0,zIndex:10});
			
			$(this).hover(function() {
				$(this).find('.hovercaption').each(function() {
					if($(this).is(":hidden")) {
						$(this).css({display:'block',bottom:'-120px'}).stop().animate({bottom:0},animate_speed,easing_method);
					} else {
						$(this).stop().animate({bottom:0},animate_speed,easing_method);
					}
				});
			},function() {
				$(this).find('.hovercaption').stop().animate({bottom:'-120px'},animate_speed,easing_method, function() { $(this).hide(); });
			});
			
			$(this).find('a.previous').click(function() {
			
				var parent = $(this).parents('.slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				current--;
				if(current<=0) current = total;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:-$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);
				
				return false;
			
			});
			
			$(this).find('a.next').click(function() {
			
				var parent = $(this).parents('.slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				current++;
				if(current>total) current = 1;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:-$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);
				
				return false;
			
			});
		
		});
	
	}
		
	/**
	 * UPDATE_GRID
	 *
	 * Update grid after logo block slider events.
	 */
	function update_grid(e) {
		
		var values=get_slider_values();
		
		$.ajax({
			type: "POST",
			url: "/stream/load",
			data: "work="+values.work+"&company="+values.company+"&now="+values.now,
			success: function(items) {
				$('#grid').html('');
				grid_full=false;
				$('footer.bottom').html('');
				$('#grid').append(items);
				$('#grid .item').hide();
				item_actions();
				place_grid_items(false);
				scroll_handler(null);
			}
		 });
		
	}
	
	/**
	 * SCROLL_HANDLER
	 *
	 * Handler browser scroll events, adjust grid accordingly.
	 */
	function scroll_handler(e) {
		if(!grid_full&&!building) {
			var bottom_offset = ($('#grid').height()+$('header.top').height()+$('footer.bottom').height()+25)-($(window).height()+$(window).scrollTop());
			if(debug) trace('bottom offset: '+bottom_offset);
			if(bottom_offset<=10) {
				if(debug) trace('bottom offset load triggered');
				load_more_items();
				if(get_total_items()>=max_items) {
					grid_full=true;
					$('footer.bottom').html('<a href="#top" class="button">Back to Top</a>');
				}
			}
		}
	}
	
	/**
	 * LOAD_MORE_ITEMS
	 *
	 * Triggered by scroll handler to load more grid items.
	 */
	function load_more_items() {
	
		if(!grid_full) {
	
			if(get_total_items()>=max_items) {
				grid_full=true;
				$('footer.bottom').html('<a href="#top" class="button">Back to Top</a>');
				return false;
			}
		
			if(!loading_items) {
		
				loading_items=true;
			
				$('footer.bottom').html('<div class="loading">loading items...</div>');
			
				var values=get_slider_values();
				
				$.ajax({
					type: "POST",
					url: "/stream/load",
					data: "work_date="+$('#grid .work:last').data('date')+"&work="+values.work+"&company_date="+$('#grid .company:last').data('date')+"&company="+values.company+"&now_date="+$('#grid .now:last').data('date')+"&now="+values.now+'&pagetype='+$('input[name=\'pagetype\']').val()+'&first='+$('input[name=\'first\']').val(),
					success: function(items) {
						if(items!=0) {
							$('#grid').find('.item').addClass('existing');
							$('#grid').append(items);
							$('#grid .item').not('.existing').hide();
							$('#grid .existing').removeClass('existing');
							item_actions();
							$('footer.bottom').html('');
							place_grid_items(false);
							scroll_handler(null);
						} else {
							grid_full=true;
							$('footer.bottom').html('<a href="#top" class="button">Back to Top</a>');
						}
					}
				});
			
			}
		
		}
		
	}
	
	/**
	 * CREATE_GRID_ARRAY
	 *
	 * Two dimensional array grid model creation.
	 */
	function create_grid_array() {
		var array = new Array(rows);
		for(var i=0; i<rows; i++) {
			array[i] = new Array(columns);
			for(var j=0; j<columns; j++) {
				array[i][j]=false;
			}
		}
		return array;
	}
	
	/**
	 * GET_ITEM_SIZE
	 *
	 * Get item size based on CSS styling.
	 */
	function get_item_size(item) {
		if($(item).hasClass('a')) return 'a';
		if($(item).hasClass('b')) return 'b';
		if($(item).hasClass('c')) return 'c';
		if($(item).hasClass('d')) return 'd';
		if($(item).hasClass('e')) return 'e';
		if($(item).hasClass('f')) return 'f';
		return '';
	}
	
	/**
	 * GET_INSERT_LOCATION
	 *
	 * Get next location to insert element. Offset allows to skip openings if desired.
	 */
	function get_insert_location(offset) {
		for(var i=0; i<rows; i++) {
			for(var j=0; j<columns; j++) {
				if(!grid[i][j]) {
					if(offset==0) {
						if(debug) trace('found location ['+i+','+j+']');
						return {row: i,column: j};
					} else {
						if(debug) trace('ignoring location ['+i+','+j+'] decrementing offset');
						offset--;
					}
				}
			}
		}
	}
	
	/**
	 * GET_TOTAL_ROWS
	 *
	 * Get total number of rows in current grid.
	 */
	function get_total_rows() {
		for(var i=0; i<rows; i++) {
			var empty=true;
			for(var j=0; j<columns; j++) {
				if(grid[i][j]) empty=false;
			}
			if(empty) return i;
		}
		return i;
	}
	
	/**
	 * GET_TOTAL_ITEMS
	 *
	 * Get total number of items in current grid.
	 */
	function get_total_items() {
		return $('#grid .item').length;
	}
	
	/**
	 * GET_TOP_POSITION
	 *
	 * Get value for CSS 'top' style for input row.
	 *
	 * @param int $row
	 * @return px
	 */
	function get_top_position(row) {
		return (row*row_height)+'px';
	}
	
	/**
	 * GET_LEFT_POSITION
	 *
	 * Get value for CSS 'left' style for input columns.
	 *
	 * @param int $column
	 * @return px
	 */
	function get_left_position(column) {
		return (column*column_width)+'px';
	}
	
	/**
	 * SET_COLUMNS
	 *
	 * Sets and adjusts the number of columns in the grid for the current
	 * window width. Called from browser resize event handler.
	 */
	function set_columns() {
		var new_columns=Math.floor(($(window).width())/column_width);
		if(debug) trace('calculated columns: '+new_columns);
		if(new_columns>=4&&new_columns!=columns) {
			if(debug) trace('changing columns: '+new_columns);
			columns=new_columns;
			var width=columns*column_width;
			$('#grid').css({width:width+'px'}); // set new grid size
			$('header.top .container').css({width:width+'px'}); // update header position
		}
		return columns;
	}
	
	/**
	 * PLACE_ITEM
	 *
	 * Place an item in the current grid at the input position.
	 *
	 * @param obj item
	 * @param int row
	 * @param int column
	 * @param boolean animate
	 */
	function place_item(item,row,column,animate) {
		var size=get_item_size(item);
		var location={top:get_top_position(row),left:get_left_position(column)};
		switch(size)
		{
		
			case 'a': // 1x1
				if( grid[row][column] ) return false; // space clear?
				grid[row][column] = 'a1';
				break;
			
			case 'b': // 1x2
				if( grid[row][column] || grid[row+1][column] ) return false; // space clear?
				if( strict && (
				
					( (column-1)>=0 && grid[row][column-1]=='b1' && grid[row+1][column-1]=='b2' ) // size b to left
					||
					( (column+1)<columns && grid[row][column+1]=='b1' && grid[row+1][column+1]=='b2' ) // size b to right
					||
					( (column-1)>=0 && grid[row][column-1]=='d1' && grid[row+1][column-1]=='d3' ) // size d to left
					||
					( (column+1)<columns && grid[row][column+1]=='d1' && grid[row+1][column+1]=='d3' ) // size d to right
					
				)) return false; // strict neighbor rules
				grid[row][column]	='b1';
				grid[row+1][column]	='b2';
				break;
			
			case 'c': // 2x1
				if( (column+1)>=columns || grid[row][column] || grid[row][column+1] ) return false; // space clear?
				if( strict && (
					
					( (row-1)>=0 && grid[row-1][column]=='c1' && grid[row-1][column+1]=='c2' ) // size c above
					||
					( (row+1)<max_rows && grid[row+1][column]=='c1' && grid[row+1][column+1]=='c2' ) // size c below
					||
					( (row-1)>=0 && grid[row-1][column]=='d3' && grid[row-1][column+1]=='d4' ) // size d above
					||
					( (row+1)<max_rows && grid[row+1][column]=='d1' && grid[row+1][column+1]=='d2' ) // size d below
					
				)) return false; // strict neighbor rules
				grid[row][column]	='c1';
				grid[row][column+1]	='c2';
				break;
				
			case 'd': // 2x2
				if( (column+1)>=columns || grid[row][column] || grid[row][column+1] || grid[row+1][column] || grid[row+1][column+1] ) return false; // space clear?
				if( strict && (
					
					( (row-1)>=0 && grid[row-1][column]=='c1' && grid[row-1][column+1]=='c2' ) // size c above
					||
					( (row+1)<max_rows && grid[row+1][column]=='c1' && grid[row+1][column+1]=='c2' ) // size c below
					||
					( (row-1)>=0 && grid[row-1][column]=='d3' && grid[row-1][column+1]=='d4' ) // size d above
					||
					( (row+1)<max_rows && grid[row+1][column]=='d1' && grid[row+1][column+1]=='d2' ) // size d below
					||
					( (column-1)>=0 && grid[row][column-1]=='b1' && grid[row+1][column-1]=='b2' ) // size b to left
					||
					( (column+1)<columns && grid[row][column+1]=='b1' && grid[row+1][column+1]=='b2' ) // size b to right
					||
					( (column-1)>=0 && grid[row][column-1]=='d1' && grid[row+1][column-1]=='d3' ) // size d to left
					||
					( (column+1)<columns && grid[row][column+1]=='d1' && grid[row+1][column+1]=='d3' ) // size d to right
					
				)) return false; // strict neighbor rules
				grid[row][column]		='d1';
				grid[row][column+1]		='d2';
				grid[row+1][column]		='d3';
				grid[row+1][column+1]	='d4';
				break;
			
			case 'e': // 2x3
				if( (column+1)>=columns || grid[row][column] || grid[row][column+1] || grid[row+1][column] || grid[row+1][column+1] || grid[row+2][column] || grid[row+2][column+1] ) return false; // space clear?
				grid[row][column]		='e1';
				grid[row][column+1]		='e2';
				grid[row+1][column]		='e3';
				grid[row+1][column+1]	='e4';
				grid[row+2][column]		='e5';
				grid[row+2][column+1]	='e6';
				break;
			
			case 'f': // 3x3
				if( (column+2)>=columns || grid[row][column] || grid[row][column+1]|| grid[row][column+2] || grid[row+1][column] || grid[row+1][column+1] || grid[row+1][column+2] || grid[row+2][column] || grid[row+2][column+1] || grid[row+2][column+2] ) return false; // space clear?
				grid[row][column]		='f1';
				grid[row][column+1]		='f2';
				grid[row][column+2]		='f3';
				grid[row+1][column]		='f4';
				grid[row+1][column+1]	='f5';
				grid[row+1][column+2]	='f6';
				grid[row+2][column]		='f7';
				grid[row+2][column+1]	='f8';
				grid[row+2][column+2]	='f9';
				break;
			
			default:
				return false;
				
		}
		if(animate) {
			$(item).show().stop().animate({top:location.top,left:location.left},animate_speed,easing_method,function() { building=false; });
		} else {
			$(item).show().css({top:location.top,left:location.left}); building=false;
		}
		return true;
	}
	
	/**
	 * PLACE_GRID_ITEMS
	 *
	 * Place all items in current grid array into display grid.
	 *
	 * @param boolean animate
	 */
	function place_grid_items(animate) {
	
		if(debug) trace('placing grid items');
	
		building=true;
	
		// hide items
		$('#grid .item').hide();
		loading_items=false;
	
		// create grid
		grid=create_grid_array();
		
		// fill 0,0 (logo)
		//grid[0][0]=1;
		//if($('header.top div.logo').hasClass('talllogo')) { grid[1][0]=1; grid[2][0]=1; }
		
		// loop and place items
		var items=$('#grid .item');
		var placed=false;
		var insert=null;
		for(var i=0; i<items.length; i++) {
			placed=false;
			for(var j=0; !placed; j++) {
				insert=get_insert_location(j);
				if(insert.row >= max_rows) break;
				placed=place_item(items[i],insert.row,insert.column,animate);
				if(placed) {
					if(debug) trace('item #'+i+' placed at ['+insert.row+','+insert.column+']');
				} else {
					if(debug) trace('item #'+i+' NOT placed at ['+insert.row+','+insert.column+']');
				}
			}
		}
		
		// update grid height
		$('#grid').css({height:(get_total_rows()*row_height)+'px'});
		if(debug) trace('new grid height: '+$('#grid').height()+'px');
		
	}
	
	/**
	 * FADEOUT_GRID
	 *
	 * Fadeout grid elements NOT e.
	 *
	 * @param object e
	 */
	function fadeout_grid(e) {
		$(e).css({zIndex:2000});
		if(!$('#grid .overlay').is(':visible')) {
			$('#grid').append('<div class="overlay"></div>');
			$('#grid .overlay').css({opacity:0}).stop().animate({opacity:0.7},Math.floor(animate_speed*2),easing_method);
		}
	}
	
	/**
	 * FADEIN_GRID
	 *
	 * Fade in grid elements NOT e.
	 *
	 * @param object e
	 */
	function fadein_grid(e) {
		$('#grid .overlay').stop().animate({opacity:0},animate_speed,easing_method, function() { $(e).css({zIndex:'auto'}); $(this).remove(); });
	}
	
	/**
	 * CLEAR_ERRORS
	 *
	 * Clear errors from form.
	 *
	 * @param object form
	 */
	function clear_errors(form) {
		$(form).find('.error').removeClass('error').unwrap().next('span.error').remove();
	}
	
	/**
	 * SET_ERROR
	 *
	 * Set a field as an error field.
	 *
	 * @param object field
	 */
	function set_error(field) {
		if($(field).is(':visible'))
			$(field).addClass('error').wrap('<div class="field" />').after('<span class="error" />').next('span.error').css({right: '50px'}).animate({right: '-32px'},Math.floor(animate_speed/2));
	}
	
	/**
	 * CLEAR_FORM
	 *
	 * Clear form data from input form.
	 *
	 * @param object form
	 */
	function clear_form(form) {
		clear_errors(form);
		$(form).find('input:visible').val('');
		$(form).find('textarea:visible').val('');
	}
	
	/**
	 * CHECK_COMMENTS_HEIGHT
	 *
	 * Set overflow on comment block for restricted height.
	 *
	 * @param object comments
	 */
	function check_comments_height(comments) {
	
		if($(comments).height()>700) {
	
			$(comments).find('ul').css({position:'absolute',top:0,left:0,margin:0}).wrap('<div class="ulscrolling" />');
			$(comments).find('div.ulscrolling').append('<div class="ulscrollbar"></div>');
			
			//
			// Set Up Scrollbar
			$(comments).find('div.ulscrollbar').slider({
				orientation: "vertical",
				min: 0,
				max: 220,
				value: 220,
				change: scroll_handler,
				slide: scroll_handler
			});
			
			//
			// Scroll Handler
			function scroll_handler( event, ui ) {
				var percentage = (220-ui.value)/220;
				var body_height = $(comments).find('ul').height();
				var position = -((body_height-300)*percentage);
				$(comments).find('ul').css({top: position+'px'});
			}
			
			//
			// Capture Mousewheel
			$(comments).find('ul').mousewheel(function(event, delta) {
				var dir = delta > 0 ? 'up' : 'down';
				var scrollbar = $(event.target).parents('div.comments').find('div.ulscrollbar');
				var value = $(scrollbar).slider("value");
				if(dir=='up') {
					value += 15;
					$(scrollbar).slider("value", value);
				} else {
					value -= 15;
					$(scrollbar).slider("value", value);
				}
				return false;
			});
		
		}
		
	}

	function check_home_slide() {
		var parent = $('#careers').find('.career-slider');
		var current = $(parent).data('current');
		if(current == 1) {
			$('#careers div.main.footer').show();
			$('#careers div.group.footer').hide();
		} else {
			$('#careers div.main.footer').hide();
			$('#careers div.group.footer').show();
		}
	}

	//
	// Careers and newsletter
	$(document).ready( function() {

			if(window.location.hash.substring(1) == 'thank-you') {
				$('#career-thank-you').show();
			}
		
			$('.career-slider').data('current',1);
			$('.career-slider').data('total',$(this).find('.slide').length);
			
			$('.career-slider').find('.slide').css({left:'-2000px',zIndex:1});
			$('.career-slider').find('.slide:first').css({left:0,zIndex:10});
			

			//
			// Section link
			$('a.careers-group-link').click(function(e) {
				e.preventDefault();
				var parent = $('#careers').find('.career-slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				
				current = $('li.' + $(this).attr('href').substring(1)).index() + 1;
				
				if(current>total) current = 1;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:-$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);

				check_home_slide();
				
				return false;

			});

			//
			// Previous Button
			$('a.careers-prev').click(function(e) {
				e.preventDefault();
				var parent = $('#careers').find('.career-slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				current--;
				if(current<=0) current = total;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:-$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);

				check_home_slide();
				
				return false;
			
			});

			// 
			// Next Button
			$('a.careers-next').click(function(e) {
				e.preventDefault();
				var parent = $('#careers').find('.career-slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				current++;
				if(current>total) current = 1;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:-$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);

				check_home_slide();
				
				return false;
			
			});

			//
			// home Link
			$('a.careers-home').click(function(e) {
				e.preventDefault();
				var parent = $('#careers').find('.career-slider');
				var current = $(parent).data('current');
				var total = $(parent).data('total');
				var slides = $(parent).find('.slide');
				var previous = current;
				
				current = 1;
				
				$(slides).css({left:'-2000px',zIndex:1});
				$(slides[previous-1]).css({left:0});
				
				$(slides[previous-1]).stop().animate({left:-$(slides[0]).width()+'px'},animate_speed,easing_method);
				$(slides[current-1]).stop().css({left:$(slides[0]).width()+'px',zIndex:10}).animate({left:0},animate_speed,easing_method);
				
				$(parent).data('current',current);

				check_home_slide();
				
				return false;

			});

			//
			// career link
			$('a.careers-link').click(function(e) {
				e.preventDefault();

				$('#career-description .career').width(642);

				var $thisCareer = $('#career-description .career.' + $(this).data('slug'));

				$('#career-description .career').hide();
				$thisCareer.show();

				$('#career-description').height($thisCareer.height() + 160);

				$('#career-description').animate({width: "762px"});

				return false;

			});

			//
			// close career link
			$('a.careers-close-link').click(function(e) {
				e.preventDefault();
				$('#career-description').animate({width: "0", minHeight: "0"});
				return false;
			});

			//
			// apply link
			$('a.apply').click( function(e) {
				$('#career-application').show();
				$('#career-application form input[name="career_id"]').val($(this).data('id'));
			});

			//
			// apply close link
			$('a.apply-close').click( function(e) {
				$('#career-application').hide();
			});

			//
			// thank you close link
			$('a.thank-you-close').click( function(e) {
				$('#career-thank-you').hide();
			});

			//
			// apply resume upload
			$('#career-application a.upload.button').click( function(e) {
				$('#resume-upload').click();
				return true;
			});
			
			//
			// custom upload button
			$('#career-application input[type="file"]').change( function(e) {
				var lastSlash = $(this).val().lastIndexOf('\\') != null ? $(this).val().lastIndexOf('\\') : $(this).val().lastIndexOf('/');
				var filename = $(this).val().substring(lastSlash + 1);
				$('a.upload.button').text(filename);
				$('#career-application #resume-text').val(filename);
				return true;
			});


			//
			// Application submit
			$('#career-application a.submit.button').click( function(e) {
				e.preventDefault();
				var $form = $(this).parents('form');
				$.post($form.attr('action'), $form.serialize(), function(data) {
					clear_errors('form');
					
					// success
					if(data.status == 200){
						$form.submit();
					}

					// failure
					else { 
						$.each(data.errors, function(field, error) {
							set_error('input[name="' + field + '"], textarea[name="' + field + '"], a.' + field);
						});
					}
				}, 'json');

			});

			//
			// Newsletter submit\
			$('form.newsletter').submit( function(e) {
				e.preventDefault();
				$.ajax({
					type: "POST",
					url: "/newsletter/subscribe",
					data: $(this).serialize(),
					success: function(data) {
						
						clear_form('form.newsletter');

						if(data.status == 500) {
							//
							// Set Error Fields
							for(error in data.errors) {
								set_error($("form.newsletter input[name='"+error+"']"));
							}
						
						} else if(data.status == 200) {
							
							$(this).html('');
							
						}
						
					},
					dataType: 'json'
				});

				return false;
		
			});

    	$('#newsletter-close').click( function() { $('#newsletter').hide(); });

	});

jQuery(function(){
	jQuery('.item .info').mouseenter(function(){
		jQuery(this).siblings('.popup').css("background-color","#fff");
		jQuery(this).siblings('.popup').children('.arrow').show();
	}).mouseleave(function(){
		jQuery(this).siblings('.popup').css("background-color","");
		jQuery(this).siblings('.popup').children('.arrow').hide();
	});
});		
