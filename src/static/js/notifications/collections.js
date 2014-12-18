var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.NotificationCollection = Backbone.Collection.extend({
        model: Phase.Models.Notification,
        url: Phase.Config.notificationsUrl
    });

})(this, Phase, Backbone, _);
