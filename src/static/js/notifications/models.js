var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Notification = Backbone.Model.extend({
        url: function() {
            var origUrl = Backbone.Model.prototype.url.call(this);
            return origUrl + (origUrl.charAt(origUrl.length - 1) === '/' ? '' : '/');
        }
    });

})(this, Phase, Backbone, _);

