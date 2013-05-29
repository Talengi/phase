(function($, undefined) {
    "use strict";

    $.fn.datatable = function(options){

        var opts = $.extend({}, options),
            $this = $(this),
            $dataHolder = $this.children('tbody');

        $this.params = {};

        // Draw the datatable
        $this.draw = function() {
            $.getJSON(opts.filterUrl, $this.params).then(function (json) {
                var template  = ["",
                    "{{#rows}}",
                    '<tr data-document-id="{{document_id}}" data-document-number="{{document_number}}">',
                    '  <td class="select"><input type="checkbox" /></td>',
                    '  <td class="favorite"><i class="{{../icon}}" data-favorite-id="{{favorite_id}}" title="{{../icon_title}}"></i></td>',
                    "  <td>{{document_number}}</td>",
                    "  <td>{{title}}</td>",
                    "  <td>{{current_revision_date}}</td>",
                    "  <td>{{current_revision}}</td>",
                    "  <td>{{status}}</td>",
                    "</tr>",
                    "{{/rows}}"
                ].join("");
                var variables = {
                    rows: json['data'],
                    icon: function() {
                        return this.favorited ? 'icon-star': 'icon-star-empty';
                    },
                    icon_title: function() {
                        return this.favorited ? 'Remove from favorites': 'Add to favorites';
                    }
                };
                $dataHolder.get(0).innerHTML = templayed(template)(variables);
            });
        };

        // Update the parameters and redraw the table
        // nameValues: [{name: 'prop1', value: "value1"},
        //              {name: 'prop2', value: "value2"}]
        $this.update = function(nameValues) {
            $this.params = nameValues;
            $dataHolder.html('');
            $this.draw();
        };

        return $this;
    };

})(jQuery);
