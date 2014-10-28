var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    /**
     * Build an object from a querystring
     */
    Phase.Models.Querystring = Backbone.Model.extend({
        constructor: function(querystring) {
            querystring = querystring || window.location.search;

            // strip everything before '?'
            var startIndex = querystring.indexOf('?');
            if (startIndex !== -1) {
                querystring = querystring.substring(startIndex + 1);
            }

            var attrs = this.parse(querystring);
            Backbone.Model.apply(this, [attrs]);
        },
        /**
         * Converts the querystring into an object.
         *
         * The `querystring` must be the part after the "?" in the url
         */
        parse: function(querystring) {
            var data = {};

            if (querystring !== '') {
                var params = querystring.split('&');
                for (var i = 0; i < params.length; i++) {
                    var param = params[i].split('=');
                    var key = decodeURIComponent(param[0]);
                    var value = decodeURIComponent(param[1]).replace(/\+/g, ' ');
                    data[key] = value;
                }
            }

            return data;
        }
    });

})(this, Phase, Backbone, _);
