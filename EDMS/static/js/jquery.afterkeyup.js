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
    }, 300);
});