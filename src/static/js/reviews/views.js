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
        initialize: function() {
            this.listenTo(this.collection, 'add', this.addReview);
            this.listenTo(this.collection, 'remove', this.removeReview);
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
        }
    });


})(this, Phase, Backbone, _);
