jQuery(function($) {

    /* Disable the whole form */
    $('#document-detail input, #document-detail textarea, #document-detail select')
        .each(function(ev) {
        $(this).attr('disabled', true);
    });

    /* Initialize datepickers and hide on select */
    $('.datepicker').datepicker().on('changeDate', function(ev) {
        $(this).datepicker('hide');
    });

    /* Related documents multiselect */
    var labels = $.makeArray($("#id_related_documents option")
                  .map(function(){ return $(this).text() }));
    $('#id_related_documents').multiselect().multiselectfilter();

});
