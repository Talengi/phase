var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = {};

    Phase.Models.Document = Backbone.Model.extend({
        idAttribute: '_id'
    });

})(this, Phase, Backbone, _);
