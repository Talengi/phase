jQuery(function($) {
    var queryParameters = '';
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
        filterUrl: config.filterUrl
    });

    /* Filter datatable's results given selected form's filters */
    var serializeTable = function(evt) {
        var parameters = $('#table-filters').serializeArray();
        datatable.update(parameters);
        /* Update the pagination link */
        queryParameters = $('#table-filters').serialize();
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
    $("#documents th").on('click', function(evt) {
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

    /* Infinite scrolling */
    $('#documents').infinitescroll({
        navSelector: "div.pagination",
        nextSelector: "div.pagination a:first",
        itemSelector: "#documents tbody",
        debug: true,
        maxPage: config.numPages,
        bufferPx: 100,
        loading: {
            finishedMsg: "",
            msg: $('<tr id="infscr-loading" class="text-center"><td colspan="7"><strong>Loading the next set of documents...</strong></td></tr>'),
        },
        path: function(pageNumber) {
            if (queryParameters === '') {
                return config.filterUrl + '?page=' + pageNumber;
            } else {
                return config.filterUrl + '?page=' + pageNumber + '&' + queryParameters;
            };
        },
    }, function (ev) {
        rowBehavior();
    });
});
