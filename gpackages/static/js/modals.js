
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

    $('#archchoice').click(function(e){
        e.preventDefault();
        var modal = $('#ArchModal');
        show_modal(modal);
        var obj = $(this).first()[0];
        var link = obj.href;
        history.pushState({modal: 'arch'}, null, link);
        return false;
    });

    $(window).on('popstate', function(){
        var current = history.state;
        var modal = $('#ArchModal');
        if(current && 'modal' in current && current.modal == 'arch'){
            show_modal(modal);
        } else {
            hide_modal(modal);
        }
    });
