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
     * Custom view to handle confirmation modals.
     */
    Phase.Views.ModalView = Backbone.View.extend({
        el: '#document-list-modal',
        events: {
            'submit form': 'submit'
        },
        initialize: function() {
            this.listenTo(dispatcher, 'onModalDisplayRequired', this.display);
        },
        show: function() {
            this.$el.modal('show');
        },
        hide: function() {
            this.$el.modal('hide');
        },
        display: function(data) {
            this.menuItem = data.menuItem;
            this.formAction = data.formAction;
            this.formData = data.formData;
            var modalId = data.modalId;
            var modalContent = $('#' + modalId).html();
            this.$el.html(modalContent);
            this.form = this.$el.find('form');
            this.show();
        },
        submit: function(event) {
            event.preventDefault();
            var form = $(event.currentTarget);
            var customFormData = form.serializeArray();
            var finalFormData = this.formData.concat(customFormData);
            this.hide();
            var data = {
                formAction: this.formAction,
                formData: finalFormData,
                menuItem: this.menuItem
            };
            dispatcher.trigger('onModalFormSubmitted', data);
        }
    });

    /**
     * Handle the different navbar buttons and form.
     */
    Phase.Views.NavbarView = Backbone.View.extend({
        el: '#table-controls',
        events: {
            'click #toggle-filters-button': 'showSearchForm',
            'click #batch-action-buttons a': 'batchActionClick'
        },
        initialize: function(options) {
            _.bindAll(this, 'batchActionSuccess');
            this.actionForm = this.$el.find('#document-list-form form').first();
            this.actionButtons = this.actionForm.find('.navbar-action');
            this.submitButtons = this.actionForm.find('[data-form-action]');
            this.dropdown = this.actionForm.find('.dropdown-form');
            this.closeBtn = this.dropdown.find('button[data-toggle=dropdown]');
            this.resultsP = this.$el.find('p#display-results');

            this.configureForm();
            this.listenTo(dispatcher, 'onRowSelected', this.setButtonsState);
            this.listenTo(dispatcher, 'onRowSelected', this.rowSelected);
            this.listenTo(dispatcher, 'onDocumentsFetched', this.renderResults);
            this.listenTo(dispatcher, 'onModalFormSubmitted', this.batchActionModalProcess);
            this.listenTo(options.search, 'change', this.cleanupSelection);
        },
        configureForm: function() {
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
        // Un-select all selected rows
        cleanupSelection: function() {
            var inputs = this.actionForm.find('input[name=document_ids]');
            inputs.remove();
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
        // Submit form upon click on a batch action
        batchActionClick: function(event) {
            event.preventDefault();
            var menuItem = $(event.target);
            var modalId = menuItem.data('modal');
            var formAction = menuItem.data('form-action');
            var formData = this.actionForm.serializeArray();
            var isAjax = menuItem.data('ajax');

            /*
             * If there is no confirmation modal, immediately submit the form.
             * Otherwise, raise an event to trigger the modal diplay.
             */
            if (modalId === '') {
                this.batchActionSubmit(formAction, formData, isAjax);
            } else {
                dispatcher.trigger('onModalDisplayRequired', {
                    menuItem: menuItem,
                    formAction: formAction,
                    formData: formData,
                    modalId: modalId
                });
            }
        },
        batchActionModalProcess: function(data) {
            var menuItem = data.menuItem;
            this.batchActionSubmit(
                data.formAction,
                data.formData,
                menuItem.data('ajax'));
        },
        batchActionSubmit: function(formAction, formData, isAjax) {
            if (isAjax) {
                $.post(formAction, formData, this.batchActionSuccess);
            } else {
                var form = $('<form />');
                form.attr('method', 'POST');
                form.attr('action', formAction);
                var inputs = _.map(formData, function(data) {
                    var input = $('<input type="hidden" />');
                    input.attr('name', data.name);
                    input.attr('value', data.value);
                    return input;
                });
                form.append(inputs);
                $('body').append(form);
                form.submit();
            }
        },
        batchActionSuccess: function(data) {
            if (data.hasOwnProperty('poll_url')) {
                var poll_url = data.poll_url;
                dispatcher.trigger('onPollableTaskStarted', {pollUrl: poll_url});
            }
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
            this.listenTo(dispatcher, 'onEscKeyPressed', this.hideSearchForm);
            this.listenTo(dispatcher, 'onAggregationsFetched', this.updateFacets);
            this.listenTo(this.model, 'change', this.synchronizeForm);

            this.synchronizeForm();

            // Check if the search form must be opened
            var cookieVal = exports.document.cookie.replace(/(?:(?:^|.*;\s*)search_form\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            console.log(cookieVal);
            if (cookieVal === 'opened') {
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
            exports.document.cookie = 'search_form=opened';
        },
        hideSearchForm: function () {
            this.$el.removeClass('active');
            exports.document.cookie = 'search_form=closed';
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
     *
     * We make sure that the "inview" event triggers only one request
     * for the next round of documents.
     */
    Phase.Views.PaginationView = Backbone.View.extend({
        el: '#documents-pagination',
        events: {
            'click': 'fetchMoreDocuments',
        },
        initialize: function() {
            _.bindAll(this, 'bindInviewEvent');

            this.listenTo(dispatcher, 'onDocumentsFetched', this.onDocumentsFetched);
        },
        onDocumentsFetched: function(data) {
            var displayed = data.displayed;
            var total = data.total;

            if (displayed < total) {
                this.showPaginationButton();
                _.delay(this.bindInviewEvent, 300);
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
            this.hidePaginationButton();
        },
        bindInviewEvent: function() {
            this.delegate('inview', '', _.bind(this.onInview, this));
        },
        unbindInviewEvent: function() {
            this.undelegate('inview');
        },
        onInview: function(event, isInView, visiblePartX, visiblePartY) {
            if (isInView) {
                this.unbindInviewEvent();
                this.$el.trigger('click');
            }
        }
    });

    /**
     * Navbar export button.
     *
     * Updates the form with hidden fields, so the current search filters
     * are passed on to the export creation view.
     *
     */
    Phase.Views.ExportFormView = Backbone.View.extend({
        el: '#export-form',
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
            this.render();
        },
        render: function() {
            var hidden = this.$el.find('input[type=hidden].filter');
            hidden.remove();

            _.each(this.model.attributes, this.addFilter, this);
        },
        addFilter: function(value, key, list) {
            var input = $('<input type="hidden" />');
            input.attr('class', 'filter');
            input.attr('name', key);
            input.val(value);
            this.$el.append(input);
        }
    });

})(this, Phase, Backbone, _);
