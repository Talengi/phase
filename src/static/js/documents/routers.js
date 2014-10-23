var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    var dispatcher = Phase.Events.dispatcher;

    Phase.Routers = {};

    /**
     * A single route router to initialize the different models and views.
     **/
    Phase.Routers.DocumentListRouter = Backbone.Router.extend({
        routes: {
            '': 'documentList'
        },
        initialize: function() {
            _.bindAll(this, 'onDocumentsFetched');
        },
        /**
         * The main document list view.
         *
         * Instanciates all required models, collections and views, and bind
         * events.
         */
        documentList: function() {
            this.tableContainer = $('#document-list-row');

            this.documentsCollection = new Phase.Collections.DocumentCollection();
            this.favoriteCollection = new Phase.Collections.FavoriteCollection(
                Phase.Config.initialFavorites
            );
            this.search = new Phase.Models.Search();

            this.tableHeaderView = new Phase.Views.TableHeaderView();
            this.tableBodyView = new Phase.Views.TableBodyView({
                collection: this.documentsCollection,
                favorites: this.favoriteCollection
            });
            this.navbarView = new Phase.Views.NavbarView();
            this.searchView = new Phase.Views.SearchView({ model: this.search });
            this.paginationView = new Phase.Views.PaginationView();

            this.listenTo(dispatcher, 'onMoreDocumentsRequested', this.onMoreDocumentsRequested);
            this.listenTo(dispatcher, 'onSort', this.onSort);
            this.listenTo(dispatcher, 'onSearch', this.onSearch);
            this.listenTo(dispatcher, 'onFavoriteSet', this.onFavoriteSet);

            this.fetchDocuments(false);
        },
        resetSearch: function() {
            this.tableContainer.scrollTop(0);
            this.search.reset();
        },
        fetchDocuments: function(reset) {
            this.documentsCollection.fetch({
                data: this.search.attributes,
                remove: false,
                reset: reset,
                success: this.onDocumentsFetched
            });
        },
        onDocumentsFetched: function() {
            var displayedDocuments = this.documentsCollection.length;
            var totalDocuments = this.documentsCollection.total;
            var aggregations = this.documentsCollection.aggregations;
            dispatcher.trigger('onDocumentsFetched', {
                displayed: displayedDocuments,
                total: totalDocuments
            });
            dispatcher.trigger('onAggregationsFetched', aggregations);
        },
        onMoreDocumentsRequested: function() {
            this.search.nextPage();
            this.fetchDocuments(false);
        },
        onSort: function(data) {
            var sortField = data.field;
            var sortDirection = data.direction;
            var prefix = sortDirection === 'down' ? '' : '-';

            this.search.set('sort_by', prefix + sortField);
            this.resetSearch();
            this.fetchDocuments(true);
        },
        onSearch: function() {
            this.resetSearch();
            this.fetchDocuments(true);
            this.updateUrl();
        },
        onFavoriteSet: function(data) {
            var document_id = data.document_id;
            var isFavorite = data.isFavorite;

            var favorite;
            if (isFavorite) {
                favorite = new Phase.Models.Favorite({document: document_id});
                this.favoriteCollection.add(favorite);
                favorite.save();
            } else {
                favorite = this.favoriteCollection.findWhere({'document': document_id});
                favorite.destroy();
            }
        },
        /**
         * Store search query parameters in url
         *
         * We don't change the whole url, only the query string. We still use
         * the Backbone router to ensure the best browser compatibility.
         *
         */
        updateUrl: function() {
            var attributes = this.search.attributes;
            var querystring = $.param(attributes);
            this.navigate('?' + querystring, {replace: true});
        }
    });
})(this, Phase, Backbone, _);
