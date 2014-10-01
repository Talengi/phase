var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Views = {};

    var dispatcher = _.clone(Backbone.Events);

    /**
     * This is the main view, englobing all other views.
     */
    Phase.Views.MainView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');

            this.documentsCollection = new Phase.Collections.DocumentCollection();

            this.tableView = new Phase.Views.TableView();
            this.paginationView = new Phase.Views.PaginationView();
            this.buttonView = new Phase.Views.ActionButtonsView();

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
        },
        selectRow: function(document) {
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: 'table#documents tbody',
        addDocumentView: function(documentView) {
            this.$el.append(documentView.render().el);
        }
    });

    /**
     * A single view in the document table
     */
    Phase.Views.RowView = Backbone.View.extend({
        tagName: 'tr',
        events: {
            'click input[type=checkbox]': 'selectRow',
        },
        template: _.template($('#documents-template').html()),
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            return this;
        },
        selectRow: function() {
            dispatcher.trigger('rowSelected', this.model);
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

    Phase.Views.ActionButtonsView = Backbone.View.extend({
        el: '#document-list-form form',
        initialize: function() {
            this.listenToOnce(dispatcher, 'rowSelected', this.activateButtons);
        },
        activateButtons: function() {
            var buttons = this.$el.find('.disabled');
            buttons.removeClass('disabled');
        }
    });

})(this, Phase, Backbone, _);
