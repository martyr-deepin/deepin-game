function change_error_css_language(lang){
    var old_error = $("#error_css_link");
    if (old_error){
    	var old_error_link = old_error.attr("href");
    	var new_error_link = old_error_link.split('-')[0] +"-" + lang + '.css';
    	$("#error_css_link").attr("href", new_error_link);
    }
}

$(document).ready(function(){
    if (window.css_language){
        change_error_css_language(window.css_language);
    }
});