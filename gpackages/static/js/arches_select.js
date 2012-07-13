var ArchesMenu = function (){
    var self = function(){};
    var cache;
    var gen_func = function(func){
        return function() { cache.each(func); }
    }
    var gen_func2 = function(dict) {
        return gen_func(function(num, obj){
            if(obj.value in dict){
                obj.checked = true;
            } else {
                obj.checked = false;
            }
        });
    }

    function create_dict(arr) {
        o = {};
        for(i=0;i<arr.length;i++){
            o[arr[i]] = true;
        }
        return o;
    }
    $.extend(self, {
        init: function (id_list, var_names) {
            cache = $(':checkbox');
            $('#reset').click(ArchesMenu.reset);
            $('#set').click(ArchesMenu.set);
            var dict, param;
            for(var i=0; i<id_list.length; i++){
                dict = create_dict(var_names[i]);
                param = 'set_' + id_list[i];
                ArchesMenu[param] = gen_func2(dict);
                $('#' + id_list[i]).click(ArchesMenu[param]);

            }
        },
        reset: gen_func(function(num, obj){
                obj.checked = false;
            }
        ),
        set: gen_func(function(num, obj){
                obj.checked = true;
            }
        )
    });
    return self;
}();

!function ($){
  $(function () {
        ArchesMenu.init(['default', 'exotic', 'fbsd', 'linux', 'solaris', 'prefix'], 
                        [default_arches, exotic_arches, fbsd_arches, linux_arches, solaris_arches, prefix_arches]);
    });
}(window.jQuery);

