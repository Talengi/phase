import factory

from .models import ValuesList, ListEntry


class ValuesListFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ValuesList

    index = factory.Sequence(lambda n: 'list_{0}'.format(n))
    name = factory.Sequence(lambda n: 'List {0}'.format(n))

    @classmethod
    def _prepare(cls, create, **kwargs):
        values = kwargs.pop('values', None)
        values_list = super(ValuesListFactory, cls)._prepare(create, **kwargs)

        if type(values) == dict:
            for key, val in values.iteritems():
                ListEntryFactory(
                    values_list=values_list,
                    index=key,
                    value=val
                )

        return values_list


class ListEntryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ListEntry

    values_list = factory.SubFactory(ValuesListFactory)
    index = factory.Sequence(lambda n: 'index_{0}'.format(n))
    value = factory.Sequence(lambda n: 'value {0}'.format(n))
