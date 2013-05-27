jQuery(function($) {
    $('#document-detail input, #document-detail textarea, #document-detail select')
        .each(function(ev) {
            $(this).attr('disabled', true);
        });

    $('.datepicker').datepicker().on('changeDate', function(ev) {
        $(this).datepicker('hide');
    });
});
