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
        },
        render: function() {
            this.collection.each(this.addNote);
            return this;
        },
        addNote: function(note) {
            var view = new Phase.Views.NoteView({ model: note });
            this.$el.append(view.render().el);
        }
    });

    Phase.Views.NoteView = Backbone.View.extend({
        tagName: 'div',
        template: _.template($('#tpl-discussion-item').html()),
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            return this;
        }
    });

})(this, Phase, Backbone, _);
