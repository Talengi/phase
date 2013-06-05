(function($, undefined) {
    "use strict";

    $.fn.datatable = function(options){

        var defaults = {
            // callback function when datatable is updated with a total rows parameter
            updated: null
        };

        var opts = $.extend(defaults, options),
            $this = $(this),
            $dataHolder = $this.children('tbody'),
            rows = [];

        // Draw the datatable
        $this.draw = function(data) {
            rows = rows.concat(data);
            var template = "{{#rows}}"+$('#documents-template tbody').html()+"{{/rows}}",
                variables = {
                    rows: data,
                    icon: function() {
                        return this.favorited ? 'icon-star': 'icon-star-empty';
                    },
                    icon_title: function() {
                        return this.favorited ? 'Remove from favorites': 'Add to favorites';
                    }
                };
            $dataHolder.get(0).innerHTML += templayed(template)(variables);
            if(opts.updated) {
                opts.updated(data, rows);
            }
        };

        var reset = function() {
            $dataHolder.html('');
            rows = [];
        }

        // clears the table and redraw the content
        // params: url parameters for ajax call
        $this.update = function(params) {
            reset();
            $this.append(params);
        };

        // append content to the table
        // params: url parameters for ajax call
        $this.append = function(params) {
            $.getJSON(opts.filterUrl, params).then(function (json) {
                $this.draw(json['data']);
            });
        }

        return $this;
    };

})(jQuery);
