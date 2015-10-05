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
            this.progress = new Phase.Models.Progress();
            this.selectedReviewsCollection = new Phase.Collections.ReviewCollection();

            this.reviewTable = new Phase.Views.TableView({
                collection: this.selectedReviewsCollection
            });
            this.actionForm = new Phase.Views.ActionForm({
                collection: this.selectedReviewsCollection,
                progress: this.progress
            });
            this.progressView = new Phase.Views.ProgressView({
                model: this.batchProgress
            });
        }
    });

})(this, Phase, Backbone, _);
