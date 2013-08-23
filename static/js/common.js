function fresh_loading(progress){
    $('#progress')[0].value = progress;
    $('#percent')[0].innerHTML = progress+"%";
}

function tabs_binding(){
    var tabs = document.getElementsByClassName('tabs')[0].children;
    for (var i=0;i<tabs.length;i++){
        tabs[i].onclick = (function (e) {
            var current_id = e.target.id;
            for (var i=0; i<tabs.length;i++){
                if (tabs[i].id == current_id){
                    tabs[i].classList.add('current');
                }
                else{
                    tabs[i].classList.remove('current');
                }
            }
        });
    }
    tabs[0].classList.add('current');
}

function gallery_change(html_path){
    $('#game-gallery').attr('src', 'file://' + html_path);
}

function append_data_to_gallery(data){
    for (var i=0; i<data.length; i++){
        var grid_div = '';
        grid_div += '<div class="item '+ data[i]['index_pic_wh'] +' caption" id="'+data[i]['type']+'-'+data[i]['id']+'">';
        grid_div += '<img src="' + data[i]['index_pic_url'] +'">';
        grid_div += '<div class="popup">';
        grid_div += '<h2><big>9</big><small>.5</small></h2>';
        grid_div += '<h3>' + data[i]['name'] + '</h3>';
        grid_div += '<h4>游戏简介：' + data[i]['summary'] + '</h4>';
        grid_div += '<span class="arrow"></span>';
        grid_div += '</div>';
        grid_div += '<a href="play://'+data[i]['id']+',';
        grid_div += data[i]['name'] +',';
        grid_div += data[i]['width'] + ',';
        grid_div += data[i]['height'] + ',';
        grid_div += data[i]['swf_game'] + ',';
        grid_div += data[i]['resizable'];
        grid_div += '" target="_blank" class="over"></a>';
        grid_div += '<a href="http://game-center.linuxdeepin.com/game/details/'+ data[i]['id'] +'" class="info"></a>';
        grid_div += '</div>';
        $('#game-gallery').contents().find('#grid').append(grid_div);
    }
}

function change_favorite_status(id, status){
    var favorite_id = '#favorite-' + id;
    if (status=='ilike'){
        $('#game-gallery').contents().find(favorite_id).removeClass('like');
        $('#game-gallery').contents().find(favorite_id).addClass('ilike');
    }
    else if (status=='like'){
        $('#game-gallery').contents().find(favorite_id).removeClass('ilike');
        $('#game-gallery').contents().find(favorite_id).addClass('like');
    }
}
