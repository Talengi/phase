var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.NoteCollection = Backbone.Collection.extend({
        model: Phase.Models.Note,
        url: Phase.Config.notesUrl
    });

})(this, Phase, Backbone, _);
