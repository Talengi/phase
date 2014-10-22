Cronjobs
########

Reindex all
-----------

Documents must be reindexed every day so that elastic search can stay in synch
with actual document data. There is a dedicated task for it::

    python manage.py reindex_all

.. WARNING::
   This task will completely delete the index and recreate it from scratch.


Crontab
-------

Setup a crontab to run scheduled tasks regularly. You must use your phase user
to run the tasks. Here is a sample crontab file::

    PYTHON="/home/phase/.virtualenvs/phase/bin/python"
    DJANGO_PATH="/home/phase/phase/src/"
    LOGS_PATH="/home/phase/django_logs/"
    DJANGO_SETTINGS="core.settings.production"

    # m h  dom mon dow   command
    01 00 * * * cd $DJANGO_PATH && $PYTHON manage.py reindex_all --noinput &>"$LOGS_PATH/reindex.log"
