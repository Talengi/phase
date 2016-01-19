var Phase = Phase || {};

jQuery(function($) {
    "use strict";

    var router = new Phase.Routers.DocumentDetailRouter();
    Backbone.history.start({
        root: Phase.Config.currentUrl
    });
});

