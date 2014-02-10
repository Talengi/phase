"use strict";

jQuery(function($) {

    // Hide and show "back to top" link on scroll events
    var configureBackToTopLink = function() {
        var $window = $(window);
        var topLink = $('#back-to-top');
        var scrollTimeout;

        // Actual scroll event handler
        var scrollHandler = function() {
            if($window.scrollTop() === 0) {
                topLink.fadeOut();
            } else {
                topLink.fadeIn();
            }
        };
        scrollTimeout = setTimeout(scrollHandler, 250);

        // Debounce the scroll handler using timeouts
        // See https://github.com/shichuan/javascript-patterns/blob/master/jquery-patterns/window-scroll-event.html
        $window.scroll(function() {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
                scrollTimeout = null;
            }
            scrollTimeout = setTimeout(scrollHandler, 250);
        });
    };
    configureBackToTopLink();
});
