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
    var main_content = document.getElementById('game-gallery');
    main_content.src = 'file://' + html_path;
}
