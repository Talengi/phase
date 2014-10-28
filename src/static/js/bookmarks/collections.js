var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.BookmarkCollection = Backbone.Collection.extend({
        model: Phase.Models.Bookmark,
        url: Phase.Config.bookmarksUrl
    });

})(this, Phase, Backbone, _);
