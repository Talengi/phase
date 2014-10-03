var without_file_label = without_file_label || '';
var with_file_label = with_file_label || '';

jQuery(function($) {
    "use strict";

    var commentInput = $('#id_comments_input');
    var submitButton = $('#review_submit');

    submitButton.val(without_file_label);
    commentInput.change(function() {
        submitButton.val(with_file_label);
    });

    var tooltips = $('span[rel=tooltip]');
    tooltips.tooltip();
});
