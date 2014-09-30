var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Views = {};

    /**
     * This is the main view, englobing all other views.
     */
    Phase.Views.MainView = Backbone.View.extend({
        initialize: function() {
            this.documentsCollection = new Phase.Collections.DocumentCollection();
            this.tableView = new Phase.Views.TableView({ collection: this.documentsCollection });

            this.documentsCollection.fetch();
        }
    });

    /**
     * A single view in the document table
     */
    Phase.Views.RowView = Backbone.View.extend({
        template: _.template($('#documents-template').html()),
        render: function() {
            return this.template(this.model.attributes);
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: 'table#documents tbody',
        initialize: function() {
            this.listenTo(this.collection, 'add', this.addDocument);
        },
        addDocument: function(document) {
            var documentView = new Phase.Views.RowView({ model: document });
            this.$el.append(documentView.render());
        }
    });

})(this, Phase, Backbone, _);
