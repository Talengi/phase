(function($, undefined) {
    "use strict";

    $.fn.datatable = function(options){

        var opts = $.extend({}, options),
            $this = $(this),
            $dataHolder = $this.children('tbody');

        $this.params = {};

        // Draw the datatable
        $this.draw = function(data) {
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
        };

        // Update the parameters and redraw the table
        // nameValues: [{name: 'prop1', value: "value1"},
        //              {name: 'prop2', value: "value2"}]
        $this.update = function(params) {
            $dataHolder.html('');
            $.getJSON(opts.filterUrl, params).then(function (json) {
                $this.draw(json['data']);
            });
        };

        $this.append = function(params) {
            $.getJSON(opts.filterUrl, params).then(function (json) {
                $this.draw(json['data']);
            });
        }

        // Update the parameters and redraw the table
        // nameValues: [{name: 'prop1', value: "value1"},
        //              {name: 'prop2', value: "value2"}]
        $this.init = function(data) {
            $dataHolder.html('');
            $this.draw(data);
        };

        return $this;
    };

})(jQuery);
