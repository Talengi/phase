var Phase = Phase || {};

jQuery(function($) {
    var router = new Phase.Routers.ReviewListRouter();
    Backbone.history.start({
        root: Phase.Config.currentUrl,
        pushState: true
    });
});

