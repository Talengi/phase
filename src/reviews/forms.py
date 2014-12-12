# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from reviews.utils import get_cached_reviews


class ReviewFormMixin(object):

    def prepare_form(self, *args, **kwargs):
        self.reviews = get_cached_reviews(self.instance)
        super(ReviewFormMixin, self).prepare_form(*args, **kwargs)
