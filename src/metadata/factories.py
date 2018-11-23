import factory

from .models import ValuesList, ListEntry


class ValuesListFactory(factory.DjangoModelFactory):
    class Meta:
        model = ValuesList

    index = factory.Sequence(lambda n: 'list_{0}'.format(n))
    name = factory.Sequence(lambda n: 'List {0}'.format(n))

    @factory.post_generation
    def values(self, create, extracted, **kwargs):
        if not create:
            return
        if type(extracted) == dict:
            for key, val in extracted.items():
                ListEntryFactory(
                    values_list=self,
                    index=key,
                    value=val
                )


class ListEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = ListEntry

    values_list = factory.SubFactory(ValuesListFactory)
    index = factory.Sequence(lambda n: 'index_{0}'.format(n))
    value = factory.Sequence(lambda n: 'value {0}'.format(n))
