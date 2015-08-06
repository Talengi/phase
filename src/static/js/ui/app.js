var Phase = Phase || {};

jQuery(function($) {
    "use strict";

    var toggleButtons = $('.toggle-content-button');
    toggleButtons.each(function(counter, button) {
        new Phase.Views.ToggleContentButton({ el: button });
    });

});

