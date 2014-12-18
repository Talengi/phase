var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.NotificationCollection = Backbone.Collection.extend({
        model: Phase.Models.Notification,
        url: Phase.Config.notificationsUrl,
        parse: function(response) {
            this.url = response.next;
            this.trigger('updateNextUrl', response.next);
            return response.results;
        }
    });

})(this, Phase, Backbone, _);
