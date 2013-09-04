function loading_flash(info){
    var flash_html = '';
	//flash_html += '<div>';
	flash_html += '<EMBED style="position:absolute;z-index:0"';
	flash_html += ' src="' + info[0] + '"';
	flash_html += ' quality=high width='+ info[1] +' height=' + info[2]; 
	flash_html += ' TYPE="application/x-shockwave-flash"';
	flash_html += ' PLUGINSPAGE="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"';
    flash_html += ' MENU="false"';
	flash_html += ' wmode="opaque">';
	//flash_html += '<div style="position:relative;filter:alpha(opacity=0);-moz-opacity:0;left:0;top:0; background:#CDEAF6;';
	//flash_html += 'width:' + info[1] +'px;height:' + info[2] + 'px;z-index:10">';
	//flash_html += '</div>';

	$('#flash').html(flash_html);
    $('#flash').width(info[1]);
    $('#flash').css('margin', 'auto');
    $('#flash').height(info[2]);
}

function padding_resize(){
    if (app_info){
        json_app_info = JSON.parse(app_info);
        if (json_app_info['resizable']){
            var new_width = json_app_info['width']/json_app_info['height']*innerHeight;
            if (new_width < innerWidth){
                $('#flash').width(new_width);
                $('#flash').height(innerHeight);
                $('EMBED').attr('width', new_width);
                $('EMBED').attr('height', innerHeight);
            }
            else{
                new_height = json_app_info['height']/json_app_info['width']*innerWidth;
                $('#flash').width(innerWidth);
                $('#flash').height(new_height);

                $('EMBED').attr('width', innerWidth);
                $('EMBED').attr('height', new_height);

                var new_padding = (innerHeight - new_height)/2;
                $('#flash').css('padding-top', new_padding);
                $('#flash').css('padding-bottom', new_padding);
            }
            return;
        }
    }

    var padding = (innerHeight - $('#flash').height())/2;
    $('#flash').css('padding-top', padding);
    $('#flash').css('padding-bottom', padding);
}

