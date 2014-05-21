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
