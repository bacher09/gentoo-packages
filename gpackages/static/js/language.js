LanguageMenu = function (){
    self = function(){};

    $.extend(self, {
        init: function () {
            $('.language').live('click', LanguageMenu.changeLanguage);
        },
        changeLanguageUrl: '/i18n/setlang/',
        changeLanguage: function (event) {
            var self = $(event.target),
                data ={
                    language: self.attr('lang')
                };

            $.post(LanguageMenu.changeLanguageUrl, data, function (data) {
                window.location.reload();
            });

            event.preventDefault();
            return false;
        }
    });
    return self;
}();

!function ($){
  $(function () {
        LanguageMenu.init();
    });
}(window.jQuery);

