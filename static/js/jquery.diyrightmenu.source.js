/**
 * this is a jquery plugin that can diy your right menu on web
 * author:i@stou.info
 * blog:www.stou.info
 * date:2012-02-27
 * version:1.0
 * how to use:
 * $('.open').diyrightmenu({
			menu: [{
				name: '菜单项名称',
				click: "write()" //点击后触发的函数
			},
			{
				hr: true
			}]
		});
 * 注意：在对象上触发了diyrightmenu以后，可以使用diySelectObject来访问这个对象。
 */
(function($) {
	$.diyrightmenu = function(){
		return this;
	}
	$.extend($.diyrightmenu, {
		init:function(){
			if ( typeof(this.insertCss) == 'undefined' ) {
				try {
					document.execCommand('BackgroundImageCache', false, true);
				} catch (e) {};
				_thisPath = (function (script, i, me) {
					for (i in script) {
						if (script[i].src && script[i].src.indexOf('diyselect') !== -1) me = script[i];
					};
					_thisScript = me || script[script.length - 1];
					me = _thisScript.src.replace(/\\/g, '/');
					return me.lastIndexOf('/') < 0 ? '.' : me.substring(0, me.lastIndexOf('/'));
				}(document.getElementsByTagName('script')));
				var css = "<style>#diyrightmenu{position:absolute!important;width:130px;padding:0 2px;border:#666 1px solid; box-shadow:0 0 3px 3px rgba(0,0,0,0.25);border-radius:3px;height:auto;overflow:hidden;display:none;z-index:999!important}#diyrightmenu ul{padding:2px 0px;margin:0;overflow:hidden;}#diyrightmenu ul li{width:108px;height:22px;line-height:22px;list-style:none;}#diyrightmenu ul li.hr{height:1px;background:-webkit-gradient(linear, left top, right top, color-stop(0, rgba(0,0,0,0.01)), color-stop(0.5, #666), color-stop(1,rgba(0,0,0,0.01)));width:100%;margin:3px 0;overflow:hidden;*margin-top:-12px;*margin-bottom:-5px}#diyrightmenu ul li a{font-size:12px;display:block;width:100%;height:100%;text-decoration:none;color:#333;padding-left:30px;cursor:default;}#diyrightmenu ul li a:hover{border-radius:2px;color:#fff;cursor:default;}</style><div id=\"diyrightmenu\"></div>";
				$('body').append(css);
				this.insertCss = true;
			}
		},
		addListener:function(element,e,fn){
			if(element.addEventListener){
				element.addEventListener(e,fn,false);
			} else {
				element.attachEvent("on" + e,fn);
			}
		},
		addPushListen:function(){
			$.diyrightmenu.addListener(document,"click",function(evt){
				var evt = window.event?window.event:evt,target=evt.srcElement||evt.target;
		　　　　	if(target.id == "diyrightmenu"){
		　　　　		return;
		　　　　	}else{
		　　　　		$('#diyrightmenu').hide();
		　　　　　　	if ( typeof(diySelectObject) != 'undefined' ) $(diySelectObject).removeClass('current');
				}
			});
		}
	});
	$.fn.diyrightmenu = function(config){
		$.diyrightmenu.init();
		$.diyrightmenu.addPushListen();
		this.each(function(i,obj){
			this.oncontextmenu=function(){
				if ( typeof(diySelectObject) != 'undefined' ) $(diySelectObject).removeClass('current');
				diySelectObject = this;
				$(this).addClass('current');
				var e = arguments[0] || window.event;
				var x = e.clientX;
				var y = e.clientY;
				var h = [];
				h.push('<ul>');
				for(i in config.menu) {
					if ( typeof(config.menu[i].hr) != 'undefined' ) {
						h.push("<li class='hr'></li>");
					} else {
						if ( typeof(config.menu[i].click) != "undefined" ) {
							click = "javascript:"+config.menu[i].click;
						}else{
							click = 'javascript:;';
						}
						if ( typeof(config.menu[i].ico) != 'undefined' && typeof(config.menu[i].ico) !=null ) {
							ico = "background-image:url("+config.menu[i].ico+");background-repeat:no-repeat;background-position:left center";
						}else{
							ico = '';
						}
						h.push("<li><a style='"+ico+"' onfocus='this.blur()' href=\""+click+"\">"+config.menu[i].name+"</a></li>");
					}
				}
				//h.push("<li class='hr'></li><li><a onfocus='this.blur()' href=\"javascript:;\" onclick=\"$('#diyrightmenu').hide();$(diySelectObject).removeClass('current');\">隐藏</a></li>");
				h.push('</ul>');
				$('#diyrightmenu').html(h.join(''));
				
				var b = document.documentElement.clientWidth;
				var c = document.documentElement.clientHeight
				var w = $('#diyrightmenu').outerWidth();
				var q = $('#diyrightmenu').outerHeight();
				if ( x+w > b ) x = x-w;
				if ( y+q > c ) y = y-q;
				$('#diyrightmenu').css({left:x+"px",top:y+"px"}).show().find('li a').click(function(){
					$('#diyrightmenu').hide();
					$(diySelectObject).removeClass('current');
				});
				$('#diyrightmenu').find('li a').each(function(i,obj){
					this.oncontextmenu=function(){return false;}
				});
				return false;
			}
			$(obj).click(function(){
				$('#diyrightmenu').hide();
				if ( typeof(diySelectObject) != 'undefined' ) $(diySelectObject).removeClass('current');
			})
		});
	};
}(jQuery));