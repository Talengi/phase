var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.ToggleContentButton = Backbone.View.extend({
        events: {
            'click': 'toggleContent'
        },
        initialize: function() {
            this.content = $(this.$el.data('target'));
        },
        toggleContent: function() {
            this.content.toggle();
        }
    });

    /**
     * A simple progress bar view, updated through a Progress model.
     */
    Phase.Views.ProgressView = Backbone.View.extend({
        el: '#progress-modal',
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
            this.listenTo(dispatcher, 'onProgressModalShow', this.show);

            this.progressBar = this.$el.find('.progress-bar');
            this.successMsg = this.$el.find('.alert-success');
        },
        render: function() {
            var progress = this.model.get('progress');
            this.progressBar.attr('aria-valuenow', progress);
            this.progressBar.css('width', progress + '%');
            return this;
        },
        show: function() {
            this.$el.modal('show');
        }
    });

})(this, Phase, Backbone, _);
