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
        className: 'note',
        template: _.template($('#tpl-discussion-item').html()),
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            return this;
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
