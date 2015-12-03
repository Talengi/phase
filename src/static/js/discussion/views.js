var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.DiscussionThreadView = Backbone.View.extend({
        el: '#discussion-body',
        initialize: function() {
            _.bindAll(this, 'addNote');
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addNote);
        },
        render: function() {
            this.$el.html('');
            this.collection.each(this.addNote);
            return this;
        },
        addNote: function(note) {
            var view = new Phase.Views.NoteView({ model: note });
            this.$el.prepend(view.render().el);
        }
    });

    Phase.Views.NoteView = Backbone.View.extend({
        tagName: 'div',
        className: 'discussion-item',
        events: {
            'click a.edit-link': 'startEdition',
            'submit form.edit-form': 'editFormSubmit',
            'click a.cancel-link': 'stopEdition',
            'click a.delete-link': 'removeNote'
        },
        template: _.template($('#tpl-discussion-item').html()),
        initialize: function() {
            this.listenTo(this.model, 'sync', this.render);
        },
        render: function() {
            this.$el.html(this.template(this.model.attributes));

            if (this.model.get('is_deleted')) {
                this.$el.addClass('deleted');
            } else {
                this.$el.removeClass('deleted');
            }

            this.readonly = this.$el.find('div.discussion-readonly');
            this.body = this.$el.find('div.discussion-body');
            this.editForm = this.$el.find('form.edit-form');
            this.textarea = this.$el.find('textarea');
            this.actions = this.$el.find('div.discussion-item-actions');

            if (Phase.Config.userId === this.model.get('author_id')) {
                if (!this.model.get('is_deleted')) {
                    this.actions.show();
                }
            }

            return this;
        },
        updateBody: function() {
            this.body.html(this.model.get('formatted_body'));
        },
        startEdition: function(event) {
            event.preventDefault();
            this.readonly.hide();
            this.editForm.show();
            this.textarea.focus();
        },
        editFormSubmit: function(event) {
            event.preventDefault();
            var body = this.textarea.val();
            this.model.save({body: body}, {wait: true});
            this.stopEdition(event);
        },
        stopEdition: function(event) {
            event.preventDefault();
            this.editForm.hide();
            this.readonly.show();
        },
        removeNote: function(event) {
            event.preventDefault();
            this.model.softDestroy();
        }
    });

    Phase.Views.DiscussionFormView = Backbone.View.extend({
        el: '#discussion-form',
        template: _.template($('#tpl-discussion-form').html()),
        events: {
            'submit form': 'onSubmit'
        },
        initialize: function() {
            _.bindAll(this, 'onSubmitError');
        },
        render: function() {
            this.$el.html(this.template());
            this.textarea = this.$el.find('textarea');
            this.alert = this.$el.find('div.alert');
        },
        onSubmit: function(event) {
            event.preventDefault();

            var body = this.textarea.val();
            this.collection.create({body: body}, {
                wait: true,
                error: this.onSubmitError
            });
            this.textarea.val('');
        },
        onSubmitError: function(event) {
            this.alert.show();
        }
    });

    Phase.Views.EmptyDiscussionFormView = Backbone.View.extend({
        el: '#discussion-form',
        render: function() {
            this.$el.html('');
        }
    });

    Phase.Views.RemarksButtonView = Backbone.View.extend({
        events: {
            'click': 'loadDiscussion'
        },
        initialize: function(options) {
            this.setElement(options.element);

            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
        },
        loadDiscussion: function() {
            this.collection.fetch({ reset: true });
        },
        render: function() {
            var badge = this.$el.find('span.badge');
            if (badge.length === 0) {
                badge = $('<span class="badge"></span>');
                this.$el.append(badge);
            }

            badge.html(this.collection.length);
            return this;
        }
    });

    Phase.Views.DiscussionView = Backbone.View.extend({
        initialize: function(options) {
            var buttons = $(options.buttons);
            var apiUrl = buttons.data('apiurl');
            var initialDiscussionLength = buttons.data('initial-discussion-length');
            this.canDiscuss = buttons.data('candiscuss');

            var discussBtn = buttons.find('button.remarks-button');
            var downloadBtn = buttons.find('a.download-comments-button');

            this.collection = new Phase.Collections.NoteCollection([], { apiUrl: apiUrl });
            this.remarksButtonView = new Phase.Views.RemarksButtonView({
                element: discussBtn,
                collection: this.collection
            });

            this.listenTo(this.collection, 'reset', this.displayDiscussion);
        },
        displayDiscussion: function() {
            this.discussionThreadView = new Phase.Views.DiscussionThreadView({
                collection: this.collection
            });
            this.discussionThreadView.render();

            if (this.canDiscuss) {
                this.discussionFormView = new Phase.Views.DiscussionFormView({
                    collection: this.collection
                });
            } else {
                this.discussionFormView = new Phase.Views.EmptyDiscussionFormView();
            }
            this.discussionFormView.render();
        }
    });

    /**
     * The global view to bootsrap the whole discussion feature.
     */
    Phase.Views.DiscussionAppView = Backbone.View.extend({
        initialize: function() {
            var discussionButtons = $('div.discussion-buttons');
            _.each(discussionButtons, function(buttons) {
                var discussionView = new Phase.Views.DiscussionView({
                    buttons: buttons
                });
                return discussionView;
            });
        }
    });

})(this, Phase, Backbone, _);
