var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    /**
     * The table containing the list of waiting reviews.
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: '#documents',
        events: {
            'click input[type=checkbox]': 'selectReview'
        },
        selectReview: function(event) {
            var target = $(event.currentTarget);
            var reviewId = target.data('review-id');
            var checked = target.is(':checked');

            if (checked) {
                this.collection.add({id: reviewId});
            } else {
                this.collection.remove(reviewId);
            }
        }
    });

    /**
     * The form with reviews batch actions.
     *
     * When a review is selected and thus added to / removed from the
     * collection, we add / delete the related hidden inputs in the form.
     */
    Phase.Views.ActionForm = Backbone.View.extend({
        el: '#review-batch-action-form',
        events: {
            'submit': 'batchCloseReviews'
        },
        initialize: function(options) {
            _.bindAll(this, 'batchSuccess', 'batchPoll', 'batchPollSuccess');

            this.progress = options.progress;
            this.button = this.$el.find('button');

            this.listenTo(this.collection, 'add', this.addReview);
            this.listenTo(this.collection, 'remove', this.removeReview);
            this.listenTo(this.collection, 'update', this.showButton);
        },
        addReview: function(model, collection, options) {
            var input = $('<input type="hidden" name="review_ids"></input>');
            input.attr('id', 'review-id-' + model.get('id'));
            input.val(model.get('id'));
            this.$el.append(input);
        },
        removeReview: function(model, collection, options) {
            var id ='#review-id-' + model.get('id');
            var input = this.$el.find(id);
            input.remove();
        },
        showButton: function(collection, options) {
            if (collection.length === 0) {
                this.button.addClass('disabled');
            } else {
                this.button.removeClass('disabled');
            }
        },
        /**
         * Submit the "close review" form as ajax.
         */
        batchCloseReviews: function(event) {
            event.preventDefault();

            var data = this.$el.serialize();
            var url = this.$el.attr('action');
            $.post(url, data, this.batchSuccess);
        },
        batchSuccess: function(data) {
            var pollUrl = data.poll_url;
            this.pollId = setInterval(this.batchPoll, 1000, pollUrl);
        },
        batchPoll: function(pollUrl) {
            $.get(pollUrl, this.batchPollSuccess);
        },
        batchPollSuccess: function(data) {
            this.progress.set('progress', data.progress);
            if (data.done) {
                clearInterval(this.pollId);
                location.reload();
            }
        }
    });


})(this, Phase, Backbone, _);
