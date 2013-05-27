(function($, undefined) {
    "use strict";

    $.fn.datatable = function(options){

        var opts = $.extend({}, options),
            $this = $(this),
            $dataHolder = $this.children('tbody');

        $this.params = {};

        // Draw the datatable
        $this.init = function() {
            $.getJSON(opts.filterUrl, $this.params).then(function (json) {
                var data = '';
                $.each(json['data'], function (key, value) {
                    data += '<tr>';
                    $.each(value, function (k, v) {
                        data += '<td>' + v + '</td>';
                    });
                    data += '</tr>';
                });
                $dataHolder.html(data);
            });
        };

        // Update the parameters and redraw the table
        // nameValues: [{name: 'prop1', value: "value1"},
        //              {name: 'prop2', value: "value2"}]
        $this.update = function(nameValues) {
            $this.params = nameValues;
            $dataHolder.html('');
            $this.init();
        };

        return $this;
    };

})(jQuery);
