var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

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


})(this, Phase, Backbone, _);
