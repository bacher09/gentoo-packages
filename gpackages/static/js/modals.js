var ModalsShow  = function(link_id_l, modal_id_l){
    var old_link = window.location.pathname;

    function show_modal(modal){
        modal.modal("show");
        modal.on('hide', function(){
            modal.off("hide");
            history.pushState({modal: false}, null, old_link);
        });

    }

    function hide_modal(modal){
        modal.off('hide');
        modal.modal('hide');
    }
    function obj_cache(){
        var list = []
        for(var i=0; i<modal_id_l.length; i++){
            list[i] = $('#' + modal_id_l[i]);
        }
        return list;
    }

    var list_m = obj_cache();

    function set_event(modal, link_selector, modal_id){
        $(link_selector).click(function(e){
            e.preventDefault();
            show_modal(modal);
            var obj = $(this)[0];
            var link = obj.href;
            history.pushState({modal: modal_id}, null, link);
            return false;
        });
    }

    function set_events(){
       for(var i=0; i<link_id_l.length; i++){  
            set_event(list_m[i], '#' + link_id_l[i], modal_id_l[i]);
        }
    }

    set_events();

    $(window).on('popstate', function(){
        var current = history.state;
        if(current && 'modal' in current && current.modal){
            var modal = list_m[modal_id_l.indexOf(current.modal)];
            show_modal(modal);
        } else {
            for(var i=0;i<list_m.length;i++){
                hide_modal(list_m[i]);
            }
        }
    });
}

$(function() {
    ModalsShow(['archchoice', 'filterchoice'], ['ArchModal', 'FilterModal']);
});
