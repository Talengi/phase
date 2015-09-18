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

            // Models and collections
            this.documentsCollection = new Phase.Collections.DocumentCollection();
            this.bookmarkCollection = new Phase.Collections.BookmarkCollection();
            this.favoriteCollection = new Phase.Collections.FavoriteCollection(
                Phase.Config.initialFavorites
            );
            var searchParams = this.extractSearchParameters();
            this.search = new Phase.Models.Search(searchParams);
            this.batchProgress = new Phase.Models.Progress();

            // Views
            var sortField = searchParams.sort_by || Phase.Config.sortBy;
            this.tableHeaderView = new Phase.Views.TableHeaderView({sortField: sortField});
            this.tableBodyView = new Phase.Views.TableBodyView({
                collection: this.documentsCollection,
                favorites: this.favoriteCollection
            });
            this.navbarView = new Phase.Views.NavbarView({ progress: this.batchProgress });
            this.progressView = new Phase.Views.ProgressView({ model: this.batchProgress });
            this.searchView = new Phase.Views.SearchView({ model: this.search });
            this.paginationView = new Phase.Views.PaginationView();
            this.bookmarkFormView = new Phase.Views.BookmarkFormView({
                collection: this.bookmarkCollection
            });
            this.bookmarkSelectView = new Phase.Views.BookmarkSelectView({
                model: this.search,
                collection: this.bookmarkCollection
            });
            this.bookmarkListView = new Phase.Views.BookmarkListView({
                collection: this.bookmarkCollection
            });
            this.exportFormView = new Phase.Views.ExportFormView({
                model: this.search
            });

            // Event binding
            this.listenTo(this.search, 'change', this.onSearch);
            this.listenTo(dispatcher, 'onMoreDocumentsRequested', this.onMoreDocumentsRequested);
            this.listenTo(dispatcher, 'onSort', this.onSort);
            this.listenTo(dispatcher, 'onFavoriteSet', this.onFavoriteSet);

            // Data fetching
            this.bookmarkCollection.reset(Phase.Config.initialBookmarks);
            this.fetchDocuments(false);
        },
        /**
         * Extract the search parameters from the query string, and returns
         * a javascript object.
         */
        extractSearchParameters: function() {
            var querystring = new Phase.Models.Querystring();
            var searchParams = querystring.attributes;

            // Pagination cannot be set by url parameters
            // because it breaks… stuff.
            delete searchParams.size;
            delete searchParams.start;

            return searchParams;
        },
        /**
         * Since we use infinite scrolling, when the search parameters are
         * updated, we need to start from page 1
         */
        resetPagination: function() {
            this.tableContainer.scrollTop(0);
            this.search.firstPage();
        },
        /**
         * Call the API to get actual search results.
         */
        fetchDocuments: function(reset) {
            this.documentsCollection.fetch({
                data: this.search.attributes,
                remove: false,
                reset: reset,
                success: this.onDocumentsFetched
            });
        },
        /**
         * When we get the search results from the API, we need to trigger
         * different events so the different views can update themselves.
         */
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
        /**
         * User scrolled all the way to the bottom of the page, let's
         * download more search results.
         */
        onMoreDocumentsRequested: function() {
            this.search.nextPage();
            this.fetchDocuments(false);
        },
        /**
         * The user clicked one of the table header to sort results.
         */
        onSort: function(data) {
            var sortField = data.field;
            var sortDirection = data.direction;
            var prefix = sortDirection === 'down' ? '' : '-';

            this.search.set('sort_by', prefix + sortField);
        },
        /**
         * The search form was updated / submitted.
         */
        onSearch: function() {
            this.resetPagination();
            this.updateUrl();
            this.fetchDocuments(true);
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
            var attributes = _.clone(this.search.attributes);

            // Pagination params should not make it to the url
            delete attributes.start;
            delete attributes.size;

            // Let's remove attributes with empty values, so the search
            // url only contains meaningful parameters
            _.each(attributes, function(value, key) {
                if ( value === "") {
                    delete attributes[key];
                }
            });
            var querystring = '?' + $.param(attributes);
            this.navigate(querystring, {replace: true});

            dispatcher.trigger('onUrlChange', querystring);
        }
    });

    /**
     * Initialize models, collections and views for the
     * document detail page.
     */
    Phase.Routers.DocumentDetailRouter = Backbone.Router.extend({
        routes: {
            '': 'documentDetail'
        },
        documentDetail: function() {
            this.discussionAppView = new Phase.Views.DiscussionAppView();
        }
    });
})(this, Phase, Backbone, _);
