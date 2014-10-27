var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Bookmark = Backbone.Model.extend({
        idAttribute: 'pk'
    });

})(this, Phase, Backbone, _);
