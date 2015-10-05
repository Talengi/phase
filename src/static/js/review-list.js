var Phase = Phase || {};

jQuery(function($) {
    "use strict";

    /* browse documents if you click on table cells */

    var clickableRow = function() {
        $("#documents tbody").on('click', 'td:not(.columnselect):not(.columnfavorite)', function(e) {
            window.location = Phase.Config.detailUrl.replace(
                'documentNumber',
                $(this).parent().data('document-key'));
        });
    };

    clickableRow();
});
