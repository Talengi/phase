var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Note = Backbone.Model.extend({
        url: function() {
            var origUrl = Backbone.Model.prototype.url.call(this);
            return origUrl + (origUrl.charAt(origUrl.length - 1) === '/' ? '' : '/');
        },
        // Send a DELETE request, but don't remove
        // object from list since this is a soft delete
        softDestroy: function() {
            var options = {};
            var model = this;
            options.success = function(resp) {
                model.set(resp);
                model.trigger('sync', model, resp, options);
            };
            var xhr = this.sync('delete', this, options);
        }
    });

})(this, Phase, Backbone, _);
