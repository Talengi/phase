var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.BookmarkFormView = Backbone.View.extend({
        el: 'form#bookmark-form',
        events: {
            'submit': 'createBookmark'
        },
        initialize: function() {
            this.urlField = this.$el.find('#id_url');
        },
        createBookmark: function(event) {
            event.preventDefault();
        }
    });

})(this, Phase, Backbone, _);
