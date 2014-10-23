var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Routers = {};

    Phase.Routers.DocumentListRouter = Backbone.Router.extend({
        routes: {
            '': 'search'
        },
        search: function() {
            console.log('search route');
        }
    });

})(this, Phase, Backbone, _);
