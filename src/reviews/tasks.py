# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType
from celery import current_task

from core.celery import app
from reviews.signals import pre_batch_review, post_batch_review, batch_item_indexed
from notifications.models import notify


@app.task
def do_batch_import(user_id, contenttype_id, document_ids):
    contenttype = ContentType.objects.get_for_id(contenttype_id)
    document_class = contenttype.model_class()

    docs = document_class.objects \
        .select_related() \
        .filter(document_id__in=document_ids)

    ok = []
    nok = []
    count = 0
    total_docs = docs.count()

    # We compute the progress as the proportion of documents for which the
    # review has started.
    # However, after all documents are treated, there is still the
    # index + refresh step which takes quite some time. So we artificially
    # increase the document count as a hackish way to never display a 100%
    # progress bar as long as the task is not truly finished.
    total_docs += 30

    pre_batch_review.send(sender=do_batch_import)

    for doc in docs:
        if doc.latest_revision.can_be_reviewed:
            doc.latest_revision.start_review()
            batch_item_indexed.send(
                sender=do_batch_import,
                document_type=doc.document.document_type(),
                document_id=doc.id,
                json=doc.latest_revision.to_json())
            ok.append(doc)
        else:
            nok.append(doc)

        count += 1
        current_task.update_state(
            state='PROGRESS',
            meta={'current': count, 'total': total_docs})

    post_batch_review.send(sender=do_batch_import, user_id=user_id)

    if len(ok) > 0:
        ok_message = ugettext('The review started for the following documents:')
        ok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in ok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            ok_message,
            ok_list
        ))

    if len(nok) > 0:
        nok_message = ugettext("We failed to start the review for the following documents:")
        nok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in nok)
        notify(user_id, '{} <ul><li>{}</li></ul>'.format(
            nok_message,
            nok_list
        ))

    return 'done'
