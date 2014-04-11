jQuery(function($) {

    $('input[data-autocomplete]').each(function() {

        var input = $(this);
        var valueField = input.data('value-field');
        var labelField = input.data('label-field');
        var searchFields = input.data('search-fields');
        var url = input.data('url');
        var mode = input.data('mode');

        input.selectize({
            valueField: valueField,
            labelField: labelField,
            searchField: searchFields,
            mode: mode,
            options: [],
            create: false,
            load: function(query, callback) {
                if (!query.length) return callback();
                $.ajax({
                    url: url,
                    type: 'GET',
                    dataType: 'json',
                    data: {
                        q: query,
                        page_limit: 10,
                    },
                    error: function() {
                        callback();
                    },
                    success: function(res) {
                        callback(res.results);
                    }
                });
            }
        });
    });
});
