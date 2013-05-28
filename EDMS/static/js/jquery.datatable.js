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
                var tr, td, data = document.createDocumentFragment();
                $.each(json['data'], function (key, value) {
                    tr = document.createElement('tr');
                    $.each(value, function (k, v) {
                        td = document.createElement('td');
                        td.innerHTML = v;
                        tr.appendChild(td);
                    });
                    data.appendChild(tr);
                });
                $dataHolder.get(0).appendChild(data);
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
