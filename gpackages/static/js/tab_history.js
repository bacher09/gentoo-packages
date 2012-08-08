$('.nav-tabs a').each(function(num, obj){
    var tab_id = obj.attributes["tab-id"].value;
    obj.id = tab_id + '_link';
});

var def_tab = $('.nav-tabs li.active').children('a')[0].id;

function activate_tab(objs){
    var obj = objs[0],
    real_url = obj.href;
    obj.href = "#" + obj.attributes["tab-id"].value;
    obj.real_url = real_url;
    objs.tab("show");
    obj.href = real_url;

}
function activate_tab_by_id(tab_id){
    activate_tab($('#' + tab_id));    
}
$('.nav-tabs a').click(function(e){ 
    e.preventDefault();
    activate_tab($(this));
});

function event_tab_show(){
    $('.nav-tabs a').on("show", function(e){ 
        history.pushState({tab: e.target.id}, null, e.target.real_url);
    });
}
event_tab_show();

function change_tab(tab_id){
    $('.nav-tabs a').off("show");
    activate_tab_by_id(tab_id);
    event_tab_show();
}

$(window).on('popstate', function(){
    var current = history.state;
    if (current && "tab" in current){
        change_tab(current.tab);
    } else {
        change_tab(def_tab);
    }
});
