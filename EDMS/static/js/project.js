$('#document-detail input, #document-detail textarea, #document-detail select')
    .each(function(ev) {
        $(this).attr('disabled', true);
    });

$('.datepicker').datepicker().on('changeDate', function(ev) {
    $(this).datepicker('hide');
});

(function($, undefined) {
    "use strict";
    var namespace = 'favorited';

    $.fn[namespace] = function(options){

        var opts = $.extend({}, options);
        var self = $(this);

        function initialize(){
            var documentId = self.data('document-id'),
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
        }
        initialize();

        return self;
    };

})(jQuery);
