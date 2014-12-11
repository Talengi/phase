var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Routers = {};

    /**
     * A single route router to initialize the different models and views.
     **/
    Phase.Routers.ReviewRouter = Backbone.Router.extend({
        routes: {
            '': 'reviewForm'
        },
        reviewForm: function() {
            this.discussionAppView = new Phase.Views.DiscussionAppView();
        }
    });
})(this, Phase, Backbone, _);
