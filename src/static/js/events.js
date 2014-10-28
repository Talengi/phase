var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Events = Phase.Events || {};

    Phase.Events.dispatcher = _.clone(Backbone.Events);
})(this, Phase, Backbone, _);
