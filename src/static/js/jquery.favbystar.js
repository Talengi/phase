(function($, undefined) {
    "use strict";

    $.fn.favbystar = function(options){

        var opts = $.extend({}, options),
            self = $(this),
            documentId = self.closest('tr').data('document-id'),
            favoriteId = self.data('favorite-id');
        if (self.hasClass('glyphicon-star')) {
            $.ajax({
                method: "POST",
                url: opts.deleteUrl.replace('0', favoriteId),
                data: {
                    csrfmiddlewaretoken: opts.csrfToken
                },
                beforeSend: function() {
                    self.removeClass("glyphicon-star")
                        .addClass("glyphicon-star-empty")
                        .attr('title', "Add to favorites");
                },
                success: function() {
                    self.data('favorite-id', '');
                }
            });
        } else {
            $.ajax({
                method: "POST",
                url: opts.createUrl,
                data: {
                    user: opts.userId,
                    'document': documentId,
                    csrfmiddlewaretoken: opts.csrfToken
                },
                beforeSend: function() {
                    self.removeClass("glyphicon-star-empty")
                        .addClass("glyphicon-star")
                        .attr('title', "Remove from favorites");
                },
                success: function(data) {
                    self.data('favorite-id', data);
                }
            });
        }
        return self;
    };

})(jQuery);
