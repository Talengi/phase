var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.DiscussionView = Backbone.View.extend({
        el: '#discussion-body',
        initialize: function() {
            _.bindAll(this, 'addNote');
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.addNote);
        },
        render: function() {
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
            this.listenTo(this.model, 'sync', this.updateBody);
        },
        render: function() {
            this.$el.html(this.template(this.model.attributes));

            this.readonly = this.$el.find('div.discussion-readonly');
            this.body = this.$el.find('div.discussion-body');
            this.editForm = this.$el.find('form.edit-form');
            this.textarea = this.$el.find('textarea');
            this.actions = this.$el.find('div.discussion-item-actions');

            if (Phase.Config.userId === this.model.get('author_id')) {
                this.actions.show();
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
            this.model.save({body: body});
            this.stopEdition(event);
        },
        stopEdition: function(event) {
            event.preventDefault();
            this.editForm.hide();
            this.readonly.show();
        },
        removeNote: function(event) {
            event.preventDefault();
            this.model.destroy();
            this.remove();
        }
    });

    Phase.Views.DiscussionFormView = Backbone.View.extend({
        el: 'form#discussion-form',
        events: {
            'submit': 'onSubmit'
        },
        initialize: function() {
            this.textarea = this.$el.find('textarea');
        },
        onSubmit: function(event) {
            event.preventDefault();

            var body = this.textarea.val();
            this.collection.create({body: body}, {wait: true});
            this.textarea.val('');
        }
    });

    Phase.Views.RemarksButtonview = Backbone.View.extend({
        el: '#remarks-button',
        initialize: function() {
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
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

})(this, Phase, Backbone, _);
