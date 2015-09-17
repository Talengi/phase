var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.TableHeaderView = Backbone.View.extend({
        el: 'table#documents thead',
        events: {
            'click #select-all': 'selectAll',
            'click th:not(#columnselect):not(#columnfavorite)': 'sort'
        },
        initialize: function(options) {
            this.sortDirection = 'down';
            this.sortField = options.sortField || Phase.Config.sortBy;

            if (this.sortField.indexOf('-') === 0) {
                this.sortField = this.sortField.substring(1);
                this.sortDirection = 'up';
            }

            this.render();
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

    /**
     * Handle the different navbar buttons and form.
     */
    Phase.Views.NavbarView = Backbone.View.extend({
        el: '#table-controls',
        events: {
            'click #toggle-filters-button': 'showSearchForm',
            'click #review-button': 'batchReview'
        },
        initialize: function(options) {
            _.bindAll(this, 'batchReviewSuccess', 'batchReviewPoll', 'batchReviewPollSuccess');
            this.actionForm = this.$el.find('#document-list-form form').first();
            this.actionButtons = this.actionForm.find('.navbar-action');
            this.dropdown = this.actionForm.find('.dropdown-form');
            this.closeBtn = this.dropdown.find('button[data-toggle=dropdown]');
            this.resultsP = this.$el.find('p#display-results');
            this.batchProgress = options.progress;

            this.configureForm();
            this.listenTo(dispatcher, 'onRowSelected', this.setButtonsState);
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
        // Activate or disactivate the action buttons
        setButtonsState: function() {
            var checked = $('#documents tr td input:checked');
            if (checked.length > 0) {
                this.actionButtons.removeClass('disabled');
            } else {
                this.actionButtons.addClass('disabled');
            }
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
        },
        /**
         * Handles the batch review button.
         *
         * We submit the form and get the task status poll url.
         * We then poll the status regularly to update the progress bar.
         * When the task is done, reload the page.
         */
        batchReview: function(event) {
            event.preventDefault();

            var data = this.actionForm.serialize();
            var url = this.actionForm.attr('action');
            $.post(url, data, this.batchReviewSuccess);
        },
        batchReviewSuccess: function(data) {
            var poll_url = data.poll_url;
            this.pollId = setInterval(this.batchReviewPoll, 1000, poll_url);
        },
        batchReviewPoll: function(poll_url) {
            $.get(poll_url, this.batchReviewPollSuccess);
        },
        batchReviewPollSuccess: function(data) {
            this.batchProgress.set('progress', data.progress);
            if (data.done) {
                clearInterval(this.pollId);
                location.reload();
            }
        }
    });

    /**
     * A simple progress bar view, updated through a Progress model.
     */
    Phase.Views.ProgressView = Backbone.View.extend({
        el: '#progress-modal',
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
            this.progressBar = this.$el.find('.progress-bar');
            this.successMsg = this.$el.find('.alert-success');
        },
        render: function() {
            var progress = this.model.get('progress');
            this.progressBar.attr('aria-valuenow', progress);
            this.progressBar.css('width', progress + '%');
            return this;
        }
    });

    Phase.Views.SearchView = Backbone.View.extend({
        el: '#search-sidebar',
        events: {
            'click #sidebar-close-btn': 'hideSearchForm',
            'submit form': 'submitForm',
            'keyup input': 'debouncedSetInput',
            'click input[type=checkbox]': 'setInput',
            'change select.filter': 'setFilter',
            'click span.glyphicon-remove': 'removeFilter',
            'click #resetForm': 'resetForm'
        },
        initialize: function() {
            _.bindAll(this, 'synchronizeAttribute', 'updateFacets', 'updateFacet');

            this.filterForm = this.$el.find('form').first();
            this.filterForm.get(0).reset();

            this.listenTo(dispatcher, 'onSearchFormDisplayed', this.showSearchForm);
            this.listenTo(dispatcher, 'onAggregationsFetched', this.updateFacets);
            this.listenTo(this.model, 'change', this.synchronizeForm);

            this.synchronizeForm();
            if (!this.isDefaultForm()) {
                this.showSearchForm();
            }
        },
        /**
         * Update the whole form to reflect the search state.
         */
        synchronizeForm: function() {
            this.filterForm.get(0).reset();
            var spans = this.$el.find('span.glyphicon-remove');
            spans.css('display', 'none');
            _.each(this.model.attributes, this.synchronizeAttribute);
        },
        /**
         * Synchronize a single field to reflect the search state.
         */
        synchronizeAttribute: function(value, field_name) {
            var field_id = '#id_' + field_name;
            var field = this.$el.find(field_id);

            if (field.length !== 0 && field.attr('type') !== 'hidden') {

                if (field.attr('type') === 'checkbox') {
                    if (typeof(value) === 'string') {
                        value = (value === 'true');
                    }
                    field.prop('checked', value);
                } else {
                    field.val(value);
                    if (value !== '') {
                        field.siblings('span').css('display', 'inline-block');
                    }
                }
            }
        },
        /**
         * Check if any field of the form has been updated, or
         * if it's still in it's default state.
         */
        isDefaultForm: function() {
            var defaults = _.result(this.model, 'defaults');
            var attributes = this.model.attributes;

            return _.isEqual(defaults, attributes);
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
        setInput: function(event) {
            var input = $(event.currentTarget);
            var name = input.attr('name');

            var val;
            if (input.attr('type') === 'checkbox') {
                val = input.prop('checked');
            } else {
                val = input.val();
            }
            this.model.set(name, val);
        },
        debouncedSetInput: _.debounce(function(event) {
            this.setInput(event);
        }, 250),
        setFilter: function(event) {
            var select = $(event.currentTarget);
            var name = select.attr('name');
            var val = select.val();
            this.model.set(name, val);
        },
        removeFilter: function(event) {
            var span = $(event.currentTarget);
            var input = span.siblings('input,select');
            var name = input.attr('name');
            this.model.unset(name);
        },
        /**
         * We reset the search. The sort parameter must not change, however.
         */
        resetForm: function() {
            var sort_by = this.model.get('sort_by');
            this.model.reset({sort_by: sort_by});
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
                option = $(option);
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
