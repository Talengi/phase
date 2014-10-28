var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = Phase.Models || {};

    Phase.Models.Document = Backbone.Model.extend({
        idAttribute: 'pk'
    });

    /**
     * Represents a single search query set of parameters
     *
     * Everytime this objects is modified ("change" event is triggered),
     * a new search query is performed.
     */
    Phase.Models.Search = Backbone.Model.extend({
        defaults: {
            search_terms: '',
            sort_by: 'document_key',
            start: 0,
            size: Phase.Config.paginateBy
        },
        /**
         * Reset the search parameters to default.
         */
        reset: function(attrs) {
            attrs = attrs || {};
            attrs = _.defaults({}, attrs, _.result(this, 'defaults'));
            this.clear({silent: true});
            this.set(attrs);
        },
        /**
         * Set the pagination params to fetch next batch of results.
         *
         * Since we don't want to replace the currently displayed results,
         * we don't trigger the "change" event, and let the calling object
         * be responsible of triggering the actual search query.
         */
        nextPage: function() {
            var start = this.get('start');
            var size = this.get('size');
            this.set('start', start + size, {silent: true});
        },
        /**
         * Set the pagination params to fetch the first results.
         *
         * Don't trigger the "change" event, so we let the calling object be
         * responsible of triggering the actual search query.
         */
        firstPage: function() {
            this.set({
                'start':this.defaults.start,
                'size': this.defaults.size
            }, {silent: true});
        }
    });

})(this, Phase, Backbone, _);
