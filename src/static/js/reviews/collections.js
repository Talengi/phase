var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.ReviewCollection = Backbone.Collection.extend({
        model: Phase.Models.Review
    });

    Phase.Collections.DistributionListCollection = Backbone.Collection.extend({
        model: Phase.Models.DistributionList,
        url: function() {
            return this.apiUrl;
        },
        initialize: function(models, options) {
            this.apiUrl = options.apiUrl;
        }
    });

})(this, Phase, Backbone, _);
