def classpath(klass):
    return '{}.{}'.format(
        klass.__module__, klass.__name__)
