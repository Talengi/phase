var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.TableView = Backbone.View.extend({
        el: 'table.table-list',
        events: {
            'click #select-all': 'selectAll',
        },
        initialize: function() {
            this.checkboxes = this.$el.find('input:checkbox');
        },
        selectAll: function(event) {
            var target = $(event.currentTarget);
            var checked = target.is(':checked');
            this.checkboxes.prop('checked', checked);
        }
    });

})(this, Phase, Backbone, _);
