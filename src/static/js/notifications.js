jQuery(function($) {
    "use strict";

    var notifButton = $('#notifications-button');
    var notifList = $('#notifications div.notification');

    // TODO Get this magic value from python instead
    var markAsReadUrl = '/api/notifications/mark_as_read/';

    // activate the button if there are existing notifications
    // it could be done in the template, but that would require
    // an additional query to count the notification number
    if(notifList.length > 0) {
        notifButton.removeClass('btn-primary');
        notifButton.addClass('btn-danger');
    }

    notifButton.one('click', function() {
        $.post(markAsReadUrl, {});
    });
});
