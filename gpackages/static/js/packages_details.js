!function ($){
    $(function() {
        $('.package a.trigger').click(function (e){
            var self = $(e.target),
            details = self.parent().next();
            $('.trigger', this).text() == '+'
                ? $('.trigger', this).text('-')
                : $('.trigger', this).text('+');

            if (details.hasClass('hide')){
                details.removeClass('hide');
                details.hide();
                details.fadeIn(200);
            }
            else details.fadeToggle(200);

            e.preventDefault();
            return false;
        });
    });
}(window.jQuery);
