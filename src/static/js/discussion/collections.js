var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.NoteCollection = Backbone.Collection.extend({
        model: Phase.Models.Note,
        url: function() {
            return this.apiUrl;
        },
        initialize: function(models, options) {
            this.apiUrl = options.apiUrl;
        }
    });

})(this, Phase, Backbone, _);
