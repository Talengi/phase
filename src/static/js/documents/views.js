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

            this.tableHeaderView = new Phase.Views.TableHeaderView();
            this.tableBodyView = new Phase.Views.TableBodyView();
            this.paginationView = new Phase.Views.PaginationView();
            this.navbarView = new Phase.Views.NavbarView();
            this.searchView = new Phase.Views.SearchView();

            this.listenTo(this.documentsCollection, 'add', this.addDocument);

            this.documentsCollection.fetch({
                success: this.render
            });
        },
        addDocument: function(document) {
            this.tableBodyView.addDocumentView(
                new Phase.Views.TableRowView({ model: document })
            );
        },
        render: function() {
            var displayedDocuments = this.documentsCollection.length;
            var totalDocuments = this.documentsCollection.total;
            this.paginationView.render(displayedDocuments, totalDocuments);

            return this;
        }
    });

    Phase.Views.TableHeaderView = Backbone.View.extend({
        el: 'table#documents thead',
        events: {
            'click #select-all': 'selectAll'
        },
        selectAll: function(event) {
            var target = $(event.currentTarget);
            var checked = target.is(':checked');
            dispatcher.trigger('selectAll', checked);
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableBodyView = Backbone.View.extend({
        el: 'table#documents tbody',
        addDocumentView: function(documentView) {
            this.$el.append(documentView.render().el);
        }
    });

    /**
     * A single view in the document table
     */
    Phase.Views.TableRowView = Backbone.View.extend({
        tagName: 'tr',
        template: _.template($('#documents-template').html()),
        events: {
            'click input[type=checkbox]': 'selectRow',
            'click td:not(.columnselect):not(.columnfavorite)': 'clickRow'
        },
        initialize: function() {
            this.listenTo(dispatcher, 'selectAll', this.setRowState);
        },
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            this.checkbox = this.$el.find('input[type=checkbox]').first();

            return this;
        },
        setRowState: function(checked) {
            if (checked != this.checkbox.is(':checked')) {
                this.checkbox.prop('checked', checked);
                this.selectRow();
            }
        },
        selectRow: function() {
            var checked = this.checkbox.is(':checked');
            if (checked) {
                this.$el.addClass('selected');
            } else {
                this.$el.removeClass('selected');
            }
            dispatcher.trigger('rowSelected', this.model, checked);
        },
        clickRow: function() {
            var detailUrl = Phase.Config.detailUrl;
            var documentUrl = detailUrl.replace(
                'document_key',
                this.model.get('document_key')
            );
            window.location = documentUrl;
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

    Phase.Views.NavbarView = Backbone.View.extend({
        el: '#table-controls',
        events: {
            'click #toggle-filters-button': 'showSearchForm'
        },
        initialize: function() {
            this.actionForm = this.$el.find('#document-list-form form').first();
            this.actionButtons = this.actionForm.find('.navbar-action');
            this.dropdown = this.actionForm.find('.dropdown-form');
            this.closeBtn = this.dropdown.find('button[data-toggle=dropdown]');

            this.configureForm();
            this.listenToOnce(dispatcher, 'rowSelected', this.activateButtons);
            this.listenTo(dispatcher, 'rowSelected', this.rowSelected);
        },
        configureForm: function() {
            // We update the form action depending on
            // the clicked button
            this.actionButtons.on('click', function(event) {
                var action = $(this).data('form-action');
                this.actionForm.attr('action', action);
            });

            // Prevent closing dropdown on any click
            this.dropdown.parent().on('hide.bs.dropdown', function(e) {
                e.preventDefault();
            });

            // Since we blocked form dropdown to be automaticaly closed,
            // we must manually bind the close button to do it
            this.closeBtn.on('click', function(event) {
                var dropdown = $(this).closest('.dropdown');
                dropdown.toggleClass('open');
            });
        },
        activateButtons: function() {
            this.actionButtons.removeClass('disabled');
        },
        rowSelected: function(document, checked) {
            if (checked) {
                var input = $('<input type="hidden" name="document_ids"></input>');
                input.attr('id', 'document-id-' + document.id);
                input.val(document.id);
                this.actionForm.append(input);
            } else {
                var input_id = '#document-id-' + document.id;
                var input = this.actionForm.find(input_id);
                input.remove();
            }
        },
        showSearchForm: function() {
            dispatcher.trigger('showSearchForm');
        }
    });

    Phase.Views.SearchView = Backbone.View.extend({
        el: '#search-sidebar',
        events: {
            'click #sidebar-close-btn': 'hideSearchForm'
        },
        initialize: function() {
            this.listenTo(dispatcher, 'showSearchForm', this.showSearchForm);
        },
        showSearchForm: function () {
            this.$el.addClass('active');
        },
        hideSearchForm: function () {
            this.$el.removeClass('active');
        }
    });

})(this, Phase, Backbone, _);
