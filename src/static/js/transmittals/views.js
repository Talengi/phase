var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    /**
     * Handle the "select all" checkbox
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: 'table.table-list',
        events: {
            'click #select-all': 'selectAll',
            'click tbody input:checkbox': 'selectOne'
        },
        initialize: function() {
            this.checkboxes = this.$el.find('tbody input:checkbox');
        },
        selectAll: function(event) {
            var target = $(event.currentTarget);
            var checked = target.is(':checked');
            var that = this;
            dispatcher.trigger('onAllRowSelected');
            this.checkboxes.each(function(index, checkbox) {
                var cb = $(checkbox);
                cb.prop('checked', checked);
                that.updateForm(cb);
            });
        },
        selectOne: function(event) {
            this.updateForm($(event.currentTarget));
        },
        updateForm: function(checkbox) {
            var checked = checkbox.prop('checked');
            var val = checkbox.val();
            dispatcher.trigger('onRowSelected', val, checked);
        }
    });


    /**
     * Updates the download form when a row is checked / unchecked
     */
    Phase.Views.DownloadFormView = Backbone.View.extend({
        el: '#download-form',
        initialize: function() {
            this.listenTo(dispatcher, 'onAllRowSelected', this.onAllRowSelected);
            this.listenTo(dispatcher, 'onRowSelected', this.onRowSelected);
        },
        onAllRowSelected: function() {
            var inputs = this.$el.find('input[name=revision_ids]');
            inputs.remove();
        },
        onRowSelected: function(rowId, checked) {
            var input;
            if (checked) {
                input = $('<input type="hidden" name="revision_ids"></input>');
                input.attr('id', 'revision-id-' + rowId);
                input.val(rowId);
                this.$el.append(input);
            } else {
                var input_id = '#revision-id-' + rowId;
                input = this.$el.find(input_id);
                input.remove();
            }
        }
    });

})(this, Phase, Backbone, _);
