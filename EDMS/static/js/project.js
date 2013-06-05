jQuery(function($) {
    var queryparams = new QueryParams();

    // initialize minimal query parameters
    queryparams.fromString($('#table-filters').serialize());


    $('#document-detail input, #document-detail textarea, #document-detail select')
        .each(function(ev) {
            $(this).attr('disabled', true);
        });

    $('.datepicker').datepicker().on('changeDate', function(ev) {
        $(this).datepicker('hide');
    });

    ///* document list *///

    /* Dealing with addition/removal of favorites */
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
        filterUrl: config.filterUrl,
        updated: function(rows, params) {
            console.log(params);
            params && params['total'] == rows.length
                ? $('.pagination a').hide()
                : $('.pagination a').show();
        }
    });

    datatable.draw(tableData);

    /* Filter datatable's results given selected form's filters */
    var serializeTable = function(evt) {
        var parameters = $('#table-filters').serializeArray();
        /* Update the pagination link */
        queryparams.fromString($('#table-filters').serialize());
        datatable.update(queryparams.data, {total: config.totalItems});
        $(this).siblings('i').css('display', 'inline-block');
        evt.preventDefault();
    };

    $("#table-filters select").on('change', serializeTable);
    $("#table-filters input").on('keyup', serializeTable);
    $("#table-filters i").on('click', function(evt) {
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
        $i.is('[class*=icon-chevron-]')
            ? $i.toggleClass("icon-chevron-up").toggleClass("icon-chevron-down")
            : $i.addClass('icon-chevron-down');
        $("#documents th i").not($i).removeClass("icon-chevron-down icon-chevron-up");
        serializeTable(evt);
    });

    /* Reseting the filtering form and thus the table's results */
    $('#resetForm').on('click', function(evt) {
        $('#table-filters').find('input:text, select').val('');
        $('#filters').find('select').val('');
        serializeTable(evt);
        $("#table-filters i").each(function(evt) {
            $(this).hide();
        });
    });

    /* select documents */

    // select rows
    var selectableRow = function() {
        var $row;
        $("#documents tbody").on('change', 'input[type=checkbox]', function(e) {
            $row = $(this).closest('tr');
            $(this).is(':checked')
                ? $row.addClass('selected')
                : $row.removeClass('selected');
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

    var clickableRow = function () {
        $("#documents tbody").on('click', 'td:not(.columnselect):not(.columnfavorite)', function(e) {
            window.location = config.detailUrl.replace(
                'documentNumber',
                $(this).parent().data('document-number')
            );
        });
    };

    var updateDocumentNumber = function () {
        $display = $("#display-results");
        $display.text(parseInt($display.text(), 10) + config.numItemsPerPage);
    };

    /* Shortcut to refresh all row's behavior when content is appened */
    var rowBehavior = function() {
        clickableRow();
        selectableRow();
        favoriteDocument();
        updateDocumentNumber();
    };
    rowBehavior();

    // click on next page appends rows to table
    $('.pagination a').on('click', function(evt) {
        var d = queryparams.data;
        // increment 'start' parameter to get next page
        d['start'] = parseInt(d['start'], 10) + parseInt(d['length'], 10);
        queryparams.update(d);
        // update the table
        datatable.append(queryparams.data);
        evt.preventDefault();
    });

    // reaching "next" button simulate a click
    $('.pagination a').on('inview', function(event, isInView, visiblePartX, visiblePartY) {
        if(isInView) {
            $(this).trigger('click');
        }
    });
});
