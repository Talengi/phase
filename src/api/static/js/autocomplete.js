jQuery(function($) {

    $('input[data-autocomplete]').each(function() {

        var input = $(this);
        var valueField = input.data('value-field');
        var labelField = input.data('label-field');
        var searchFields = input.data('search-fields');
        var url = input.data('url');
        var mode = input.data('mode');
        var initialId = input.data('initial-id');
        var initialLabel = input.data('initial-label');

        input.selectize({
            valueField: valueField,
            labelField: labelField,
            searchField: searchFields,
            mode: mode,
            dataAttr: 'data-data',
            create: false,
            options: [],
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

        if(!initialId.hasOwnProperty('length')) {
            initialId = [initialId];
            initialLabel = [initialLabel];
        }

        var options = [];
        for (var i = 0 ; i < initialId.length ; i++) {
            var option = {};
            option[valueField] =  initialId[i];
            option[labelField] =  initialLabel[i];
            options.push(option);
        }
        input[0].selectize.addOption(options);
        input[0].selectize.setValue(initialId);
    });
});
