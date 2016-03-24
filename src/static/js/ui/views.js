var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Views = Phase.Views || {};

    Phase.Views.ToggleContentButton = Backbone.View.extend({
        events: {
            'click': 'toggleContent'
        },
        initialize: function() {
            this.content = $(this.$el.data('target'));

            this.listenTo(dispatcher, 'onEscKeyPressed', this.hideContent);
        },
        toggleContent: function() {
            this.content.toggle();
        },
        hideContent: function() {
            this.content.hide();
        }
    });

    /**
     * A simple progress bar view, updated through a Progress model.
     */
    Phase.Views.ProgressView = Backbone.View.extend({
        el: '#progress-modal',
        initialize: function() {
            this.listenTo(this.model, 'onPollStarted', this.show);
            this.listenTo(this.model, 'change', this.render);

            this.progressBar = this.$el.find('.progress-bar');
            this.successMsg = this.$el.find('.alert-success');
        },
        render: function() {
            var progress = this.model.get('progress');
            this.progressBar.attr('aria-valuenow', progress);
            this.progressBar.css('width', progress + '%');
            return this;
        },
        show: function() {
            this.$el.modal('show');
        }
    });

    Phase.Views.ActionMenuView = Backbone.View.extend({
        events: {
            'click a': 'actionClick'
        },
        initialize: function(options) {
            _.bindAll(this, 'actionSuccess');

            this.actionForm = this.$el.closest('form');

            this.listenTo(dispatcher, 'onModalFormSubmitted', this.actionModalProcess);
        },
        // Submit form upon click on a batch action
        actionClick: function(event) {
            event.preventDefault();
            var menuItem = $(event.target);
            var modalId = menuItem.data('modal');
            var actionHref = menuItem.attr('href');
            var isAjax = menuItem.data('ajax');
            var method = menuItem.data('method');

            var formData = [];
            if (this.actionForm.length > 0) {
                formData = this.actionForm.serializeArray();
            }

            /*
             * If there is no confirmation modal, immediately submit the form.
             * Otherwise, raise an event to trigger the modal diplay.
             */
            if (modalId === '') {
                this.actionSubmit(actionHref, formData, method, isAjax);
            } else {
                dispatcher.trigger('onModalDisplayRequired', {
                    menuItem: menuItem,
                    formAction: actionHref,
                    formData: formData,
                    modalId: modalId,
                });
            }
        },
        actionModalProcess: function(data) {
            var menuItem = data.menuItem;
            this.actionSubmit(
                data.formAction,
                data.formData,
                menuItem.data('method'),
                menuItem.data('ajax'));
        },
        actionSubmit: function(actionHref, formData, method, isAjax) {
            if (isAjax) {
                $.ajax(actionHref, {
                    method: method,
                    data: formData,
                    success: this.actionSuccess
                });
            } else {
                if (method === 'GET') {
                    exports.location.href = actionHref;
                } else {
                    var form = $('<form />');
                    form.attr('method', 'POST');
                    form.attr('action', actionHref);
                    var inputs = _.map(formData, function(data) {
                        var input = $('<input type="hidden" />');
                        input.attr('name', data.name);
                        input.attr('value', data.value);
                        return input;
                    });
                    form.append(inputs);
                    $('body').append(form);
                    form.submit();
                }
            }
        },
        actionSuccess: function(data) {
            if (data.hasOwnProperty('poll_url')) {
                var poll_url = data.poll_url;
                dispatcher.trigger('onPollableTaskStarted', {pollUrl: poll_url});
            }
        }

    });

    /**
     * Custom view to handle confirmation modals.
     */
    Phase.Views.ModalView = Backbone.View.extend({
        el: '#base-modal',
        events: {
            'submit form': 'submit'
        },
        initialize: function() {
            this.listenTo(dispatcher, 'onModalDisplayRequired', this.display);
        },
        show: function() {
            this.$el.modal('show');
        },
        hide: function() {
            this.$el.modal('hide');
        },
        display: function(data) {
            this.menuItem = data.menuItem;
            this.formAction = data.formAction;
            this.formData = data.formData;
            var modalId = data.modalId;
            var modalContent = $('#' + modalId).html();
            this.$el.html(modalContent);
            this.form = this.$el.find('form');
            this.show();
        },
        isValid: function(form){
            var checkboxes = form.find(".js-required-checkbox");
            if (checkboxes.length > 0){
                if (!checkboxes.is(":checked")){
                    alert('At least one checkbox must be checked');
                    return false;
                }
            }
            return true;
        },
        submit: function(event) {
            event.preventDefault();
            var form = $(event.currentTarget);

            if (!this.isValid(form)){return false}

            var customFormData = form.serializeArray();
            var finalFormData = this.formData.concat(customFormData);
            this.hide();
            var data = {
                formAction: this.formAction,
                formData: finalFormData,
                menuItem: this.menuItem
            };
            dispatcher.trigger('onModalFormSubmitted', data);
        }
    });
})(this, Phase, Backbone, _);
