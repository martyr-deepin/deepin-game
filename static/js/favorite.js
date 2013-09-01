function favorite_action(e, id){
    var favorite_id = '#favorite-' + id;
    if ($(favorite_id).hasClass('like')){
        $(favorite_id).removeClass('like');
        $(favorite_id).addClass('ilike');
        $(favorite_id).text(function(i, origText){
            return Number(origText)+1;
        });
        alert('favorite://'+id);
        var favorite_url = 'http://' + location.host + '/game/analytics/?type=favorite&appid=' + id;
        $.get(favorite_url, function(data,status){
            //alert('Data: ' + data + '\nStatus: ' + status);
        });
    }
    else if (($(favorite_id).hasClass('ilike'))){
        $(favorite_id).removeClass('ilike');
        $(favorite_id).addClass('like');
        $(favorite_id).text(function(i, origText){
            return Number(origText)-1;
        });
        alert('unfavorite://'+id);
        var favorite_url = 'http://' + location.host + '/game/analytics/?type=unfavorite&appid=' + id;
        $.get(favorite_url, function(data,status){
            //alert('Data: ' + data + '\nStatus: ' + status);
        });
    }
}
