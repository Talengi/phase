var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.ReviewCollection = Backbone.Collection.extend({
        model: Phase.Models.Review
    });

})(this, Phase, Backbone, _);
