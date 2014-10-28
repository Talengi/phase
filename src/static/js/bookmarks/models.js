var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Bookmark = Backbone.Model.extend({
        idAttribute: 'pk',
        fromForm: function(form) {
            var data = form.serializeArray();
            var self = this;
            _.each(data, function(field) {
                self.set(field.name, field.value);
            });
        },
    });

})(this, Phase, Backbone, _);
