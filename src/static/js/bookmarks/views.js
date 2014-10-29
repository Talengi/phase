var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    /**
     * The bookmark selection view.
     *
     * When a bookmark is selected, the corresponding search is performed
     * immediately, and the url is updated.
     *
     * When the search form is updated while a bookmark is selected, it becomes
     * unselected
     */
    Phase.Views.BookmarkSelectView = Backbone.View.extend({
        el: 'select#id_bookmark',
        events: {
            'change': 'selectBookmark'
        },
        initialize: function() {
            _.bindAll(this, 'addBookmark');

            this.listenTo(this.model, 'change', this.deselectBookmark);
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addBookmark);
            this.listenTo(this.collection, 'destroy', this.removeBookmark);
        },
        render: function() {
            this.collection.each(this.addBookmark);
            return this;
        },
        addBookmark: function(bookmark) {
            var option = $('<option></option>');
            option.attr('id', 'bookmark_' + bookmark.get('id'));
            option.val(bookmark.get('url'));
            option.text(bookmark.get('name'));

            this.$el.append(option);
        },
        /**
         * A bookmark was removed. Remove the corresponing option.
         */
        removeBookmark: function(bookmark) {
            var option = this.$el.find('option#bookmark_' + bookmark.get('id'));
            option.remove();
        },
        /**
         * A bookmark was selected.
         *
         * Create an actual Bookmark objects and update the search.
         *
         */
        selectBookmark: function(option) {
            var querystring = this.$el.val();
            if (querystring !== '') {
                var bookmark = new Phase.Models.Bookmark();
                bookmark.fromUrl(querystring);

                this.stopListening(this.model, 'change');
                this.model.reset(bookmark.attributes);
                this.listenTo(this.model, 'change', this.deselectBookmark);
            }
        },
        deselectBookmark: function() {
            this.$el.val('');
        }
    });

    /**
     * The bookmark creation form view.
     *
     * A new bookmark is created and stored with ajax when the form is
     * submitted.
     *
     */
    Phase.Views.BookmarkFormView = Backbone.View.extend({
        el: 'form#bookmark-form',
        events: {
            'submit': 'createBookmark'
        },
        initialize: function() {
            var currentUrl = window.location.pathname + window.location.search;
            this.urlField = this.$el.find('#id_url');
            this.urlField.val(currentUrl);
            this.nameField = this.$el.find('#id_name');
            this.modal = this.$el.find('.modal');

            this.listenTo(dispatcher, 'onUrlChange', this.onUrlChange);
        },
        createBookmark: function(event) {
            event.preventDefault();

            var formData = this.$el.serializeArray();
            var data = {};
            _.each(formData, function(datum) {
                data[datum.name] = datum.value;
            });
            this.collection.create(data, {wait: true});
            this.nameField.val('');
            this.modal.modal('hide');
        },
        /**
         * When the url is updated, update the form hidden input.
         */
        onUrlChange: function() {
            var currentUrl = window.location.pathname + window.location.search;
            this.urlField.val(currentUrl);
        }
    });

    /**
     * Bookmark deletion view
     */
    Phase.Views.BookmarkListView = Backbone.View.extend({
        el: 'ul#bookmark-list',
        initialize: function() {
            _.bindAll(this, 'addBookmark');

            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addBookmark);
        },
        render: function() {
            this.collection.each(this.addBookmark);
            return this;
        },
        addBookmark: function(bookmark) {
            var view = new Phase.Views.BookmarkListItemView({ model: bookmark });
            this.$el.append(view.render().el);
        }
    });

    /**
     * A single line in the bookmark list view.
     */
    Phase.Views.BookmarkListItemView = Backbone.View.extend({
        tagName: 'li',
        className: 'list-group-item',
        template: _.template($('#tpl-bookmark-item').html()),
        events: {
            'click button': 'deleteBookmark'
        },
        initialize: function() {
            this.listenTo(this.model, 'destroy', this.remove);
        },
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            return this;
        },
        deleteBookmark: function() {
            this.model.destroy();
        }
    });

})(this, Phase, Backbone, _);
