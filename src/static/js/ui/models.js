var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Models = Phase.Models || {};

    /**
     * Used to share data between a form handler and a progress bar view.
     */
    Phase.Models.Progress = Backbone.Model.extend({
        defaults: {
            progress: 0,
            pollUrl: ''
        },
        initialize: function() {
            this.listenTo(dispatcher, 'onPollableTaskStarted', this.startPolling);
            _.bindAll(this, 'taskPoll', 'taskPollSuccess');
        },
        startPolling: function(data) {
            this.set('pollUrl', data.pollUrl);
            this.set('progress', 0);
            this.pollId = setInterval(this.taskPoll, 1000);
            this.trigger('onPollStarted');
        },
        url: function() {
            return this.get('pollUrl');
        },
        taskPoll: function(poll_url) {
            $.get(this.url(), this.taskPollSuccess);
        },
        taskPollSuccess: function(data) {
            this.set('progress', data.progress);
            if (data.done) {
                clearInterval(this.pollId);
                dispatcher.trigger('onPollableTaskEnded');
                location.reload(true);
            }
        }
    });

     Phase.Models.Activity = Backbone.Model.extend({
         defaults: {
            text: '',
            created_on: ''
        }
     });

    Phase.Models.Activities = Backbone.Collection.extend({
    model: Phase.Models.Activity,
    initialize: function(props) {
        this.url = props.url;
    },
    parse: function(response){
        if(response.next &&  response.next !== this.url){
            this.url = response.next;
        }else{
            this.url= null;
        }
        return response.results;
    },
    getNext: function(pageLimit){
        this.fetch({add: true, page_limit : pageLimit, remove: false});
    }
});

})(this, Phase, Backbone, _);
