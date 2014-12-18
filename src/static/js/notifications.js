jQuery(function($) {
    "use strict";

    var notifButton = $('#notifications-button');
    var notifList = $('#notifications div.notification');

    // TODO Get this magic value from python instead
    var markAsReadUrl = '/api/notifications/mark_as_read/';

    notifButton.one('click', function() {
        $.post(markAsReadUrl, {});
    });
});
