// TODO Use backbone to backbort this old behavior

jQuery(function ($) {

    "use strict";

    /* Disable the whole form and let value selectable and copy/pastable by users*/
    var documentDetail = $('#document-detail');
    documentDetail.find('input, textarea')
        .each(function (el) {
            $(this).attr('readonly', true);
            $(this).attr('disabled', false);
        });
    var inputTpl = _.template('<input maxlength="250" class="form-control" value="<%= text  %>"/>');
    documentDetail.find('select')
        .each(function (el) {
            var selected = $(this).find(":selected").text();
            var text = inputTpl({text: selected});
            $(this).after(text);
            $(this).hide();
        });

    /* Initialize datepickers and hide on select */
    $('.dateinput:not([readonly]):not(:disabled)').datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function (ev) {
        $(this).datepicker('hide');
    });

    /* Related documents multiselect */
    var labels = $.makeArray($("#id_related_documents option")
        .map(function () {
            return $(this).text();
        }));
    $('#id_related_documents').multiselect().multiselectfilter();

    /* File uploads */
    $('[data-dismiss]').click(function (e) {
        e.preventDefault();
        var target = $(this).data('dismiss');
        var field = $('[name="' + target + '"]');

        // Delete the field content
        // See http://stackoverflow.com/a/13351234/665797
        field.wrap('<form>').closest('form').get(0).reset();
        field.unwrap();

        $(this).closest('div').find('.fileupload-preview').html('');
    });

    /* Form in dropdown menu */
    $('a.dropdown-submit').click(function (e) {
        var form = $(this).prev('form');
        form.submit();
    });

    // Hide and show "back to top" link on scroll events
    var configureBackToTopLink = function () {
        var $window = $(window);
        var topLink = $('#back-to-top');

        // Actual scroll event handler
        var scrollHandler = function () {
            if ($window.scrollTop() === 0) {
                topLink.fadeOut();
            } else {
                topLink.fadeIn();
            }
        };

        // Binding to the scroll event is awful for performances
        var scrollInterval = setInterval(scrollHandler, 3000);
    };
    configureBackToTopLink();

    $('body').scrollspy({target: '#document-sidebar'});

    var tooltips = $('span[rel=tooltip]');
    tooltips.tooltip();
});
