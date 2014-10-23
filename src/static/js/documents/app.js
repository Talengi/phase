var Phase = Phase || {};

jQuery(function($) {
    var mainView = new Phase.Views.MainView();
    Backbone.history.start({
        root: Phase.Config.currentUrl,
        pushState: true,
        silent: true
    });
});
