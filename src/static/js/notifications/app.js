var Phase = Phase || {};

jQuery(function($) {
    "use strict";

    var notifButton = $('#notifications-button');
    var notifList = $('#notifications div.notification');

    // TODO Get this magic value from python instead
    var markAsReadUrl = '/api/notifications/mark_as_read/';

    notifButton.one('click', function() {
        $.post(markAsReadUrl, {});
    });

    var collection = new Phase.Collections.NotificationCollection();
    var view = new Phase.Views.NotificationsModalView({ collection: collection });
});
