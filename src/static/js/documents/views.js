var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = {};

    Phase.Views.TableHeaderView = Backbone.View.extend({
        el: 'table#documents thead',
        events: {
            'click #select-all': 'selectAll',
            'click th:not(#columnselect):not(#columnfavorite)': 'sort'
        },
        initialize: function() {
            this.sortDirection = 'down';
            this.sortField = Phase.Config.sortBy;
        },
        selectAll: function(event) {
            var target = $(event.currentTarget);
            var checked = target.is(':checked');
            dispatcher.trigger('onAllRowsSelected', checked);
        },
        sort: function(event) {
            var th = $(event.currentTarget);
            var sortBy = th.data('sortby');

            if (sortBy === this.sortField) {
                this.switchSortDirection();
            } else {
                this.setSortField(sortBy);
            }

            this.render();
            dispatcher.trigger('onSort', {
                field: this.sortField,
                direction: this.sortDirection
            });
        },
        switchSortDirection: function() {
            this.sortDirection = this.sortDirection === 'up' ? 'down' : 'up';
        },
        setSortField: function(field) {
            this.sortDirection = 'down';
            this.sortField = field;
        },
        render: function() {
            var spans = this.$el.find('th:not(#columnselect):not(#columnfavorite) span');
            spans.remove();

            var span = '<span class="glyphicon glyphicon-chevron-' + this.sortDirection + '"></span>';
            var field = this.$el.find('#column' + this.sortField).first();
            field.append($(span));

            return this;
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableBodyView = Backbone.View.extend({
        el: 'table#documents tbody',
        initialize: function(options) {
            _.bindAll(this, 'addDocument');
            this.favorites = options['favorites'];
            this.listenTo(this.collection, 'add', this.addDocument);
            this.listenTo(this.collection, 'reset', this.addAllDocuments);
        },
        addDocument: function(document) {
            var view = new Phase.Views.TableRowView({
                model: document,
                isFavorite: this.isFavorite(document)
            });
            this.$el.append(view.render().el);
        },
        addAllDocuments: function() {
            this.$el.empty();
            this.collection.map(this.addDocument);
        },
        isFavorite: function(document) {
            // TODO This is probably not the most efficienc way
            // to do this.
            var fav = this.favorites.findWhere({'document': document.get('document_pk')});
            return fav !== undefined;
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
            'click td:not(.columnselect):not(.columnfavorite)': 'clickRow',
            'click td.columnfavorite': 'toggleFavorite'
        },
        initialize: function(options) {
            this.listenTo(dispatcher, 'onAllRowsSelected', this.setRowState);
            this.isFavorite = options['isFavorite'];
        },
        render: function() {
            var attributes = this.stringAttributes();
            this.$el.html(this.template(attributes));
            this.checkbox = this.$el.find('input[type=checkbox]').first();
            this.favoriteIcon = this.$el.find('td.columnfavorite span').first();

            if (this.isFavorite) {
                this.favoriteIcon.removeClass('glyphicon-star-empty');
                this.favoriteIcon.addClass('glyphicon-star');
            }

            return this;
        },
        /**
         * TODO use a template?
         */
        stringAttributes: function() {
            var attributes = {};
            _.each(this.model.attributes, function(value, key) {
                switch (typeof value) {
                    case 'boolean':
                        value = value ? 'Yes' : 'No';
                        break;
                }
                attributes[key] = value;
            });
            return attributes;
        },
        setRowState: function(checked) {
            if (checked !== this.checkbox.is(':checked')) {
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
            dispatcher.trigger('onRowSelected', this.model, checked);
        },
        clickRow: function() {
            var detailUrl = Phase.Config.detailUrl;
            var documentUrl = detailUrl.replace(
                'document_key',
                this.model.get('document_key')
            );
            window.location = documentUrl;
        },
        toggleFavorite: function() {
            this.isFavorite = !this.isFavorite;
            dispatcher.trigger('onFavoriteSet', {
                'document_id': this.model.get('document_pk'),
                'isFavorite': this.isFavorite
            });
            if (this.isFavorite) {
                this.favoriteIcon.addClass('glyphicon-star');
                this.favoriteIcon.removeClass('glyphicon-star-empty');
            } else {
                this.favoriteIcon.removeClass('glyphicon-star');
                this.favoriteIcon.addClass('glyphicon-star-empty');
            }
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
            this.resultsP = this.$el.find('p#display-results');

            this.configureForm();
            this.listenToOnce(dispatcher, 'onRowSelected', this.activateButtons);
            this.listenTo(dispatcher, 'onRowSelected', this.rowSelected);
            this.listenTo(dispatcher, 'onDocumentsFetched', this.renderResults);
        },
        configureForm: function() {
            // We update the form action depending on
            // the clicked button
            var self = this;
            this.actionButtons.on('click', function(event) {
                var action = $(this).data('form-action');
                self.actionForm.attr('action', action);
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
            var input;
            if (checked) {
                input = $('<input type="hidden" name="document_ids"></input>');
                input.attr('id', 'document-id-' + document.id);
                input.val(document.id);
                this.actionForm.append(input);
            } else {
                var input_id = '#document-id-' + document.id;
                input = this.actionForm.find(input_id);
                input.remove();
            }
        },
        showSearchForm: function() {
            dispatcher.trigger('onSearchFormDisplayed');
        },
        renderResults: function(data) {
            var results;
            if (data.displayed <= 1) {
                results = '' + data.displayed + ' document on ' + data.total;
            } else {
                results = '' + data.displayed + ' documents on ' + data.total;
            }
            this.resultsP.html(results);
        }
    });

    Phase.Views.SearchView = Backbone.View.extend({
        el: '#search-sidebar',
        events: {
            'click #sidebar-close-btn': 'hideSearchForm',
            'submit form': 'submitForm',
            'keyup input': 'debouncedSearch',
            'change select': 'setFilter',
            'click span.glyphicon-remove': 'removeFilter',
            'click #resetForm': 'resetForm'
        },
        initialize: function() {
            _.bindAll(this, 'updateFormAttribute', 'updateFacets', 'updateFacet');

            this.filterForm = this.$el.find('form').first();
            this.filterForm.get(0).reset();

            this.listenTo(dispatcher, 'onSearchFormDisplayed', this.showSearchForm);
            this.listenTo(dispatcher, 'onAggregationsFetched', this.updateFacets);
            this.listenTo(this.model, 'change', this.updateForm);
        },
        updateForm: function() {
            _.map(this.model.attributes, this.updateFormAttribute);
        },
        updateFormAttribute: function(value, field_name) {
            var field_id = '#id_' + field_name;
            var field = this.$el.find(field_id);
            field.val(value);
        },
        showSearchForm: function () {
            this.$el.addClass('active');
        },
        hideSearchForm: function () {
            this.$el.removeClass('active');
        },
        submitForm: function(event) {
            event.preventDefault();
        },
        search: function() {
            this.stopListening(this.model, 'change');
            this.model.fromForm(this.filterForm);
            this.listenTo(this.model, 'change', this.updateForm);

            dispatcher.trigger('onSearch');
        },
        debouncedSearch: _.debounce(function() {
            this.search();
        }, 250),
        setFilter: function(event) {
            var select = $(event.currentTarget);
            if (select.val() !== '') {
                select.siblings('span').css('display', 'inline-block');
            } else {
                select.siblings('span').css('display', 'none');
            }

            this.search();
        },
        removeFilter: function(event) {
            var span = $(event.currentTarget);
            var select = span.siblings('select');
            select.val('');
            span.css('display', 'none');
            this.search();
        },
        resetForm: function() {
            var spans = this.$el.find('span.glyphicon-remove');
            spans.css('display', 'none');
            this.debouncedSearch();
        },
        updateFacets: function(aggregations) {
            _.each(aggregations, this.updateFacet);
        },
        /**
         * Get the buckets values from Elasticsearch aggregations, and
         * update the filter fields display accordingly.
         */
        updateFacet: function(buckets, facet) {
            // Let's get the field, and loop on every "option" tag
            var field = this.filterForm.find('#id_' + facet).first();
            var options = field.children('option');
            var option_text_re = /^(.+) \(\d+\)$/i;
            _.each(options, function(option) {
                var option = $(option);
                var text = option.text();
                var val = option.val();

                // This is the "--------" first option
                if (val === '') {
                    return;
                }


                // Strips existing count suffix
                var match = option_text_re.exec(text);
                if (match !== null) {
                    text = match[1];
                }

                // ES doesn'nt return a value if the bucket is empty
                var bucket_number = buckets[val];
                if (bucket_number === undefined) {
                    bucket_number = 0;
                }

                text = text + ' (' + bucket_number + ')';
                option.text(text);
            });
        }
    });

    /**
     * "Load more documents" button an infinite scrolling.
     */
    Phase.Views.PaginationView = Backbone.View.extend({
        el: '#documents-pagination',
        events: {
            'click': 'fetchMoreDocuments',
            'inview': 'onInview'
        },
        initialize: function() {
            this.listenTo(dispatcher, 'onDocumentsFetched', this.onDocumentsFetched);
        },
        onDocumentsFetched: function(data) {
            var displayed = data.displayed;
            var total = data.total;

            if (displayed < total) {
                this.showPaginationButton();
            } else {
                this.hidePaginationButton();
            }
        },
        showPaginationButton: function() {
            this.$el.show();
        },
        hidePaginationButton: function() {
            this.$el.hide();
        },
        fetchMoreDocuments: function() {
            dispatcher.trigger('onMoreDocumentsRequested');
        },
        onInview: function(event, isInView, visiblePartX, visiblePartY) {
            if (isInView) {
                this.$el.trigger('click');
            }
        }
    });

})(this, Phase, Backbone, _);
