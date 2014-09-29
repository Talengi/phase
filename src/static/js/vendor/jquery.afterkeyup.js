(function($) {
    /**
    Triggers an "afterkeyup" event on any input or textarea.
    The event is triggers when stopped typing for 400ms.
    */
    var delay = (function() {
        var timer = 0;
        return function(callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();
    $('input,textarea').keyup(function() {
        var self = this;
        delay(function() {
            $(self).trigger('afterkeyup');
        }, 400);
    });
})(jQuery);