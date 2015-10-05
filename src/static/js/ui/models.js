var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    /**
     * Used to share data between a form handler and a progress bar view.
     */
    Phase.Models.Progress = Backbone.Model.extend({
        defaults: {
            progress: 0
        }
    });

})(this, Phase, Backbone, _);
