var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Routers = {};

    Phase.Routers.ReviewListRouter = Backbone.Router.extend({
        routes: {
            '': 'reviewList'
        },
        reviewList: function() {
        }
    });

})(this, Phase, Backbone, _);
