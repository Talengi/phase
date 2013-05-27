(function($, undefined) {
    "use strict";

    $.fn.favbystar = function(options){

        var opts = $.extend({}, options),
            self = $(this),
            documentId = self.data('document-id'),
            favoriteId = self.data('favorite-id');

        if (self.hasClass('icon-star')) {
            $.ajax({
                type: "POST",
                url: opts.deleteUrl.replace('0', favoriteId),
                data: {
                    csrfmiddlewaretoken: opts.csrfToken
                },
                beforeSend: function() {
                    self.removeClass("icon-star")
                        .addClass("icon-star-empty")
                        .attr('title', "Add to favorites");
                }
            }).done(function( favoriteId ) {
                self.data('favorite-id', '');
            });
        } else {
            $.ajax({
                type: "POST",
                url: opts.createUrl,
                data: {
                    user: opts.userId,
                    document: documentId,
                    csrfmiddlewaretoken: opts.csrfToken
                },
                beforeSend: function( favoriteId ) {
                    self.removeClass("icon-star-empty")
                        .addClass("icon-star")
                        .attr('title', "Remove from favorites");
                }
            }).done(function( favoriteId ) {
                self.data('favorite-id', favoriteId);
            });
        }
        return self;
    };

})(jQuery);
