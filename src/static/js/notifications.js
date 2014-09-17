jQuery(function($) {
    "use strict";

    var notifButton = $('#notifications-button');
    var markAsReadUrl = '/api/notifications/mark_as_read/';

    notifButton.one('click', function() {
        $.post(markAsReadUrl, {})
    });
});
