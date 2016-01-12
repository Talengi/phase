var Phase = Phase || {};

jQuery(function($) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    var toggleButtons = $('.toggle-content-button');
    toggleButtons.each(function(counter, button) {
        new Phase.Views.ToggleContentButton({ el: button });
    });

    $(document).keyup(function(event) {
        if (event.keyCode === 27) {
            dispatcher.trigger('onEscKeyPressed');
        }
    });
});

