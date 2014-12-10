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
            this.noteCollection = new Phase.Collections.NoteCollection();
            this.discussionView = new Phase.Views.DiscussionView({
                collection: this.noteCollection
            });
            this.discussionFormView = new Phase.Views.DiscussionFormView({
                collection: this.noteCollection
            });
            this.remarksButtonView = new Phase.Views.RemarksButtonview({
                collection: this.noteCollection
            });
            this.noteCollection.fetch({ reset: true });
        }
    });
})(this, Phase, Backbone, _);
