(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};
    Phase.Models = Phase.Models || {};
    Phase.Views = Phase.Views || {};

    Phase.Models.Document = Backbone.Model.extend({
        idAttribute: '_id'
    });

    Phase.Collections.DocumentCollection = Backbone.Collection.extend({
        model: Phase.Models.Document,
        url: Phase.Config.searchUrl,
        parse: function(response) {
            this.total = response.total;
            return response.data
        }
    });

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

    Phase.Views.RowView = Backbone.View.extend({
        template: _.template($('#documents-template').html()),
        render: function() {
            return this.template(this.model.attributes);
        }
    });

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

    exports.Phase = Phase;
})(this, Phase, Backbone, _);

jQuery(function($) {
    var mainView = new Phase.Views.MainView();
});

jQuery(function($) {
    var queryparams = new QueryParams();

    // initialize minimal query parameters
    queryparams.fromString($('#table-filters').serialize());
    isFirstPage = true;

    /* Dealing with addition/removal of favorites */
    var updateDocumentNumber = function(display, total) {
        $("#display-results").text(display);
        $("#total-results").text(total);
    };

    var favoriteDocument = function() {
        $('#documents tbody').on('click', '.columnfavorite', function(e) {
            $(this).children().favbystar({
                userId: config.userId,
                csrfToken: config.csrfToken,
                createUrl: config.createUrl,
                deleteUrl: config.deleteUrl
            });
        });
    };

    /* Initializing the datatable */
    var datatable = $('#documents').datatable({
        filterUrl: config.searchUrl,
        updated: function(rows, params) {
            params && params['total'] == rows.length ? $('.pagination a').hide() : $('.pagination a').show();
            // update headers information
            if (params) {
                updateDocumentNumber(params['display'], params['total']);
            } else {
                var displayItems = Math.min(config.numItemsPerPage, config.totalItems);
                updateDocumentNumber(displayItems, config.totalItems);
            }
        }
    });
    datatable.draw(tableData['data']);


    /* Filter datatable's results given selected form's filters */
    var serializeTable = function(evt) {
        var parameters = $('#table-filters').serializeArray();
        /* Update the pagination link */
        queryparams.fromString($('#table-filters').serialize());
        datatable.update(queryparams.data, {
            total: config.totalItems
        });
        $(this).siblings('span').css('display', 'inline-block');
        evt.preventDefault();
    };

    $("#table-filters").on('submit', function(event) {
        return event.preventDefault();
    });
    $("#table-filters select").on('change', serializeTable);
    $("#table-filters input").on('afterkeyup', serializeTable);
    $("#table-filters span").on('click', function(evt) {
        $(this).siblings('select,input:text').val('');
        serializeTable(evt);
        $(this).hide();
    });
    $("#documents th:not(#columnselect):not(#columnfavorite)").on('click', function(evt) {
        var $this = $(this);
        var sortBy = $this.data("sortby");
        var $sortBy = $('#id_sort_by');
        var direction = (sortBy == $sortBy.val()) ? '-' : '';
        $('#id_sort_by').val(direction + sortBy);
        $i = $this.children();
        $i.is('[class*=glyphicon-chevron-]') ? $i.toggleClass("glyphicon-chevron-up").toggleClass("glyphicon-chevron-down") : $i.addClass('glyphicon glyphicon-chevron-down');
        $("#documents th span").not($i).removeClass("glyphicon-chevron-down glyphicon-chevron-up");
        serializeTable(evt);
    });

    /* Reseting the filtering form and thus the table's results */
    $('#resetForm').on('click', function(evt) {
        $('#table-filters').find('input:text, select').val('');
        $('#filters').find('select').val('');
        serializeTable(evt);
        $("#table-filters span").each(function(evt) {
            $(this).hide();
        });
    });

    /* select documents */

    // select rows
    var selectableRow = function() {
        var $row;
        var form = $('.navbar-form');
        var buttons = $('.navbar-action');
        var close_btn = $('.dropdown-form button[data-toggle=dropdown]');

        // Update form action depending on clicked button
        buttons.on('click', function(event) {
            var action = $(this).data('form-action');
            form.attr('action', action);
        });

        // Prevent closing dropdown on any click
        $('.dropdown-form').parent().on('hide.bs.dropdown', function(e) {
            e.preventDefault();
        });

        // Since we blocked form dropdown to be automaticaly closed,
        // we must manually bind the close button to do it
        close_btn.on('click', function(event) {
            var dropdown = $(this).closest('.dropdown');
            dropdown.toggleClass('open');
        });

        $("#documents tbody").on('change', 'input[type=checkbox]', function(e) {
            buttons.removeClass('disabled');
            $row = $(this).closest('tr');
            var documentId = $row.data('metadata-id');
            if ($(this).is(':checked')) {
                $row.addClass('selected');
                var input = document.createElement('input');
                input.id = "document-id-"+documentId;
                input.name = "document_ids";
                input.type = "hidden";
                input.value = documentId;
                form[0].appendChild(input);
            } else {
                $row.removeClass('selected');
                $(".navbar-form input#document-id-"+documentId).remove();
            }
        });
    };

    // select/deselect all rows
    var selected, checkbox;
    $('#select-all').on('change', function(e) {
        selected = $(this).is(':checked');
        checkbox = $("#documents tbody input[type=checkbox]");
        checkbox.prop('checked', selected);
        checkbox.trigger('change');
    });

    /* browse documents if you click on table cells */

    var clickableRow = function() {
        $("#documents tbody").on('click', 'td:not(.columnselect):not(.columnfavorite)', function(e) {
            window.location = config.detailUrl.replace(
                'documentNumber',
                $(this).parent().data('document-key'));
        });
    };

    /* Shortcut to refresh all row's behavior when content is appened */
    var rowBehavior = function() {
        clickableRow();
        selectableRow();
        favoriteDocument();
    };
    rowBehavior();

    // click on next page appends rows to table
    $('.pagination a').on('click', function(evt) {

        if (!isFirstPage) {
            var d = queryparams.data;
            // increment 'start' parameter to get next page
            d['start'] = parseInt(d['start'], 10) + parseInt(d['length'], 10);
            queryparams.update(d);
            isFirstPage = false;
        }
        // update the table
        datatable.append(queryparams.data);
        evt.preventDefault();
    });

    // reaching "next" button simulate a click
    $('.pagination a').on('inview', function(event, isInView, visiblePartX, visiblePartY) {
        if (isInView) {
            $(this).trigger('click');
        }
    });

    // off canvas
    $('[data-toggle=offcanvas]').click(function() {
        var offcanvas = $('.sidebar-offcanvas');
        offcanvas.toggleClass('active');
    });
});
