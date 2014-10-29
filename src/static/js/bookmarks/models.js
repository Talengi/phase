var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Bookmark = Backbone.Model.extend({
        url: function() {
            var origUrl = Backbone.Model.prototype.url.call(this);
            return origUrl + (origUrl.charAt(origUrl.length - 1) === '/' ? '' : '/');
        },
        fromUrl: function(querystring) {
            var q = new Phase.Models.Querystring(querystring);
            this.set(q.attributes);
        },
        fromForm: function(form) {
            var data = form.serializeArray();
            var self = this;
            _.each(data, function(field) {
                self.set(field.name, field.value);
            });
        },
    });

})(this, Phase, Backbone, _);
