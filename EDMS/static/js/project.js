jQuery(function($) {
    $('#document-detail input, #document-detail textarea, #document-detail select')
        .each(function(ev) {
            $(this).attr('disabled', true);
        });

    $('.datepicker').datepicker().on('changeDate', function(ev) {
        $(this).datepicker('hide');
    });

    ///* document list *///

    /* Dealing with addition/removal of favorites */
    $('#documents tbody').on('click', '.favorite', function(e) {
        $(this).children().favbystar({
            userId: config.userId,
            csrfToken: config.csrfToken,
            createUrl: config.createUrl,
            deleteUrl: config.deleteUrl
        });
    });

    /* Initializing the datatable */
    var datatable = $('#documents').datatable({
        filterUrl: config.filterUrl
    });

    /* Filter datatable's results given selected form's filters */
    var serializeTable = function(evt) {
        datatable.update($('#table_filter').serializeArray());
        $(this).siblings('i').css('display', 'inline-block');
        evt.preventDefault();
    };

    $("#table_filter select").on('change', serializeTable);
    $("#table_filter input").on('keyup', serializeTable);
    $("#table_filter i").on('click', function(evt) {
        $(this).siblings('select,input:text').val('');
        serializeTable(evt);
        $(this).hide();
    });

    /* Reseting the filtering form and thus the table's results */
    $('#resetForm').on('click', function(evt) {
        $('#table_filter').find('input:text, select').val('');
        $('#filters').find('select').val('');
        serializeTable(evt);
        $("#table_filter i").each(function(evt) {
            $(this).hide();
        });
    });

    /* select documents */

    // select rows
    var $row;
    $("#documents tbody").on('change', 'input[type=checkbox]', function(e) {
        $row = $(this).closest('tr');
        $(this).is(':checked')
            ? $row.addClass('selected')
            : $row.removeClass('selected');
    });

    // select/deselect all rows
    var selected, checkbox;
    $('#select-all').on('change', function(e) {
        selected = $(this).is(':checked');
        checkbox = $("#documents tbody input[type=checkbox]");
        checkbox.prop('checked', selected);
        checkbox.trigger('change');
    });

    /* browse documents if you click on table cells */

    $("#documents tbody").on('click', 'td:not(.select):not(.favorite)', function(e) {
        window.location = config.detailUrl.replace(
            'documentNumber',
            $(this).parent().data('document-number')
        );
    });

});
