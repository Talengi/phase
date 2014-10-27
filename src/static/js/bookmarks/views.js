var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.BookmarkSelectView = Backbone.View.extend({
        el: 'select#id_bookmark',
        events: {
            'change': 'bookmarkSelected'
        },
        initialize: function() {
            _.bindAll(this, 'addBookmark');

            this.listenTo(this.collection, 'add', this.addBookmark);

            this.render();
        },
        render: function() {
            this.collection.each(this.addBookmark);
            return this;
        },
        addBookmark: function(bookmark) {
            var option = $('<option></option>');
            option.attr('id', bookmark.get('id'));
            option.val(bookmark.get('url'));
            option.text(bookmark.get('name'));

            this.$el.append(option);
        },
        bookmarkSelected: function(option) {
        }
    });

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
