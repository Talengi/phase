var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var oldSync = Backbone.sync;
    Backbone.sync = function(method, model, options){
        options.beforeSend = function(xhr){
            xhr.setRequestHeader('X-CSRFToken', Phase.Config.csrfToken);
        };
        return oldSync(method, model, options);
    };
})(this, Phase, Backbone, _);

