var Phase = Phase || {};

jQuery(function($) {
    //var mainView = new Phase.Views.MainView();
    var router = new Phase.Routers.DocumentListRouter();
    Backbone.history.start({
        root: Phase.Config.currentUrl,
        pushState: true
    });
});
