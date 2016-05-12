# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory

from accounts.factories import UserFactory
from distriblists.models import DistributionList


class DistributionListReviewerFactory(factory.DjangoModelFactory):
    class Meta:
        model = DistributionList.reviewers.through

    user = factory.SubFactory(UserFactory)


class DistributionListFactory(factory.DjangoModelFactory):
    class Meta:
        model = DistributionList

    name = factory.Sequence(lambda n: 'Distrib list {}'.format(n))
    leader = factory.SubFactory(UserFactory)
    approver = factory.SubFactory(UserFactory)
    reviewer1 = factory.RelatedFactory(DistributionListReviewerFactory, 'distributionlist')
    reviewer2 = factory.RelatedFactory(DistributionListReviewerFactory, 'distributionlist')
    reviewer3 = factory.RelatedFactory(DistributionListReviewerFactory, 'distributionlist')

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.categories.add(category)

    @factory.post_generation
    def reviewers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for reviewer in extracted:
                self.reviewers.add(reviewer)
