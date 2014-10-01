var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Views = {};

    /**
     * This is the main view, englobing all other views.
     */
    Phase.Views.MainView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');

            this.documentsCollection = new Phase.Collections.DocumentCollection();

            this.tableView = new Phase.Views.TableView();
            this.paginationView = new Phase.Views.PaginationView();

            this.listenTo(this.documentsCollection, 'add', this.addDocument);
            this.documentsCollection.fetch({
                success: this.render
            });
        },
        addDocument: function(document) {
            this.tableView.addDocumentView(
                new Phase.Views.RowView({ model: document })
            );
        },
        render: function() {
            var displayedDocuments = this.documentsCollection.length;
            var totalDocuments = this.documentsCollection.total;
            this.paginationView.render(displayedDocuments, totalDocuments);

            return this;
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: 'table#documents tbody',
        addDocumentView: function(documentView) {
            this.$el.append(documentView.render());
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
     * A small view to handle the pagination text.
     * "xxx documents on yyy"
     */
    Phase.Views.PaginationView = Backbone.View.extend({
        el: 'p#display-results',
        render: function(displayed, total) {
            var results;
            if (displayed <= 1) {
                results = '' + displayed + ' document on ' + total;
            } else {
                results = '' + displayed + ' documents on ' + total;
            }
            this.$el.html(results);

            return this;
        }
    });

})(this, Phase, Backbone, _);
