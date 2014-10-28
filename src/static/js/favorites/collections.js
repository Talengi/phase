var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Collections = Phase.Collections || {};

    Phase.Collections.FavoriteCollection = Backbone.Collection.extend({
        model: Phase.Models.Favorite,
        url: Phase.Config.favoriteUrl
    });

})(this, Phase, Backbone, _);

