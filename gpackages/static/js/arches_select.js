var ArchesMenu = function (){
    var self = function(){};
    var cache, default_arch_obj;
    var gen_func = function(func){
        return function() { cache.each(func); }
    }
    function create_dict(arr){
        o = {};
        for(i=0;i<arr.length;i++){
            o[arr[i]] = true;
        }
        return o;
    }
    $.extend(self, {
        init: function () {
            $('#reset').live('click', ArchesMenu.reset);
            $('#set').live('click', ArchesMenu.set);
            $('#default').live('click', ArchesMenu.set_default);
            cache = $(':checkbox');
            default_arch_obj = create_dict(default_arches);
        },
        reset: gen_func(function(num, obj){
                obj.checked = false;
            }
        ),
        set: gen_func(function(num, obj){
                obj.checked = true;
            }
        ),
        set_default: gen_func(function(num, obj){
                if(obj.value in default_arch_obj){
                    obj.checked = true;
                } else {
                    obj.checked = false;
                }
            }
        )
    });
    return self;
}();

!function ($){
  $(function () {
        ArchesMenu.init();
    });
}(window.jQuery);

