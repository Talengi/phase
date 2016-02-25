# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from documents.factories import DocumentFactory
from default_documents.tests.test import ContractorDeliverableTestCase
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from transmittals.factories import (
    TransmittalFactory, TrsRevisionFactory, create_transmittal)
from transmittals.models import TrsRevision
from transmittals.forms import (
    OutgoingTransmittalForm, OutgoingTransmittalRevisionForm)


class TransmittalListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')
        self.url = reverse('transmittal_list')

    def test_empty_transmittal_list(self):
        res = self.client.get(self.url)
        self.assertContains(res, 'There are no transmittals here')

    def test_transmittal_list(self):
        TransmittalFactory(document__category=self.category)
        TransmittalFactory(document__category=self.category)
        TransmittalFactory(document__category=self.category)
        res = self.client.get(self.url)
        self.assertNotContains(res, 'There are no transmittals here')
        self.assertContains(res, 'tr class="document_row"', 3)


class BaseTransmittalDiffViewTests(TestCase):

    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.transmittal = TransmittalFactory(
            document__category=self.category)
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')
        self.url = reverse('transmittal_diff', args=[
            self.transmittal.pk,
            self.transmittal.document_key])

    def create_lines(self, nb_existing=1, nb_new=1, **kwargs):
        """Create `nb_existing` + `nb_new` lines in the transmittal."""
        doc = DocumentFactory(
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category)
        metadata = doc.metadata

        arguments = {
            'transmittal': self.transmittal,
            'document': doc,
            'document_key': doc.document_key,
            'title': doc.title,
            'is_new_revision': False,
            'category': self.category,
        }
        arguments.update(kwargs)

        # Existing revisions
        for i in range(nb_existing):
            rev = ContractorDeliverableRevisionFactory(
                metadata=metadata)

            arguments.update({'revision': rev.revision})
            TrsRevisionFactory(**arguments)

        metadata.latest_revision = rev
        metadata.save()

        arguments.update({'is_new_revision': True})

        # New revisions
        for i in range(nb_new):
            arguments.update({'revision': rev.revision + i + 1})
            TrsRevisionFactory(**arguments)

        return doc


class TransmittalDiffViewTests(BaseTransmittalDiffViewTests):

    def test_transmittal_detail_view(self):
        self.create_lines(2, 3)
        res = self.client.get(self.url)
        self.assertContains(res, 'tr class="document_row"', 5)

    def test_new_updated_labels(self):
        self.create_lines(3, 4)
        res = self.client.get(self.url)
        self.assertContains(res, 'span class="label label-warning"', 4)
        self.assertContains(res, 'span class="label label-primary"', 3)

    def test_accepted_icons(self):
        self.create_lines(1, 1)
        self.create_lines(2, 2, accepted=True)
        self.create_lines(3, 3, accepted=False)

        res = self.client.get(self.url)
        self.assertContains(res, 'glyphicon-empty', 2)
        # "+ 2" because there are icons elsewhere in the page
        self.assertContains(res, 'glyphicon-ok', 4 + 2)
        self.assertContains(res, 'glyphicon-remove', 6 + 1)


class TrsRevisionDiffViewTests(BaseTransmittalDiffViewTests):

    def setUp(self):
        super(TrsRevisionDiffViewTests, self).setUp()
        self.doc = self.create_lines(1, 2)
        self.trs_revisions = self.transmittal.trsrevision_set.order_by('revision')

    def test_diff_with_existing_revision(self):
        trs_revision = self.trs_revisions[0]
        trs_revision.title = 'New title yeah!'
        trs_revision.save()

        res = self.client.get(trs_revision.get_absolute_url())
        self.assertContains(res, escape(self.doc.title))
        self.assertContains(res, trs_revision.title)

    def test_diff_with_single_new_revision(self):
        trs_revision = self.trs_revisions[1]
        trs_revision.title = 'New title yeah!'
        trs_revision.save()

        res = self.client.get(trs_revision.get_absolute_url())
        self.assertContains(res, escape((self.doc.title)))
        self.assertContains(res, trs_revision.title)

    def test_diff_with_new_revisions(self):
        new_revision = self.trs_revisions[1]
        new_revision.title = 'Old title yeah!'
        new_revision.save()

        newest_revision = self.trs_revisions[2]
        newest_revision.title = 'New title yeah!'
        newest_revision.save()

        res = self.client.get(newest_revision.get_absolute_url())
        self.assertContains(res, new_revision.title)
        self.assertContains(res, newest_revision.title)

    def test_accept_changes(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.accepted)

        self.client.post(trs_revision.get_absolute_url(), {'accept': 'accept'})
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertTrue(trs_revision.accepted)

    def test_refuse_changes(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.accepted)

        self.client.post(trs_revision.get_absolute_url(), {'refuse': 'refuse'})
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertFalse(trs_revision.accepted)

    def test_leave_comment(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.comment)

        self.client.post(trs_revision.get_absolute_url(), {
            'accept': 'accept',
            'comment': 'Gloubiboulga'
        })
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertEqual(trs_revision.comment, 'Gloubiboulga')


class TestPrepareTransmittalTests(ContractorDeliverableTestCase):

    def setUp(self):
        super(TestPrepareTransmittalTests, self).setUp()
        self.prepare_transmittals_url = reverse('transmittal_prepare', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])

    def test_prepare_documents(self):
        under_prep_qs = ContractorDeliverable.objects \
            .filter(latest_revision__under_preparation_by=self.user)

        docs = [self.create_doc() for _ in range(5)]
        self.assertEqual(under_prep_qs.count(), 0)

        meta_ids = [doc.get_metadata().id for doc in docs]
        self.client.post(self.prepare_transmittals_url, {
            'document_ids': meta_ids
        }, follow=True)

        self.assertEqual(under_prep_qs.count(), 5)


class AckReceiptOfTransmittalTests(TestCase):
    def setUp(self):
        self.trs = create_transmittal()
        self.category = self.trs.document.category
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('transmittal_ack_of_receipt', args=[
            self.category.organisation.slug,
            self.category.slug,
            self.trs.document.document_key
        ])

    def test_non_contractor_acks_receipt(self):
        """Non contractor cannot ack receipt of transmittals."""
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 403)

    def test_acks_receipt(self):
        self.assertIsNone(self.trs.ack_of_receipt_date)
        self.assertIsNone(self.trs.ack_of_receipt_author)

        self.user.is_external = True
        self.user.save()
        res = self.client.post(self.url, follow=True)
        self.assertEqual(res.status_code, 200)

        self.trs.refresh_from_db()
        self.assertIsNotNone(self.trs.ack_of_receipt_date)
        self.assertEqual(self.trs.ack_of_receipt_author, self.user)

    def test_acks_receipt_twice_fails(self):
        self.user.is_external = True
        self.user.save()

        self.trs.ack_receipt(self.user)

        res = self.client.post(self.url, follow=True)
        self.assertEqual(res.status_code, 403)


class BatchAckOfTransmittalsTests(TestCase):
    def setUp(self):
        self.trs = create_transmittal()
        self.category = self.trs.document.category
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('transmittal_batch_ack_of_receipt', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])

    def test_internal_user_cannot_ack_transmittal(self):
        res = self.client.post(self.url, {'document_ids': [self.trs.document_id]})
        self.assertEqual(res.status_code, 403)

    def test_acks_receipt(self):
        self.user.is_external = True
        self.user.save()

        res = self.client.post(
            self.url,
            {'document_ids': [self.trs.document_id]},
            follow=True)
        self.assertEqual(res.status_code, 200)

        self.trs.refresh_from_db()
        self.assertIsNotNone(self.trs.ack_of_receipt_date)
        self.assertEqual(self.trs.ack_of_receipt_author, self.user)


class TransmittalErrorNotificationTests(TestCase):
    def setUp(self):
        self.trs = create_transmittal()
        self.rev = self.trs.latest_revision
        self.category = self.trs.document.category
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.trs.recipient.users.add(self.user)
        self.client.login(email=self.user.email, password='pass')
        self.url = self.trs.document.get_edit_url()

        form = OutgoingTransmittalForm(
            self.trs.__dict__,
            category=self.category,
            instance=self.trs)
        form.full_clean()
        self.form_data = form.cleaned_data
        rev_form = OutgoingTransmittalRevisionForm(
            self.rev.__dict__,
            category=self.category,
            instance=self.rev)
        rev_form.full_clean()
        self.form_data.update(rev_form.cleaned_data)

    def test_no_error_no_notification(self):
        self.assertEqual(self.user.notification_set.count(), 0)
        res = self.client.post(self.url, self.form_data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(self.user.notification_set.count(), 0)

    def test_on_error_send_notification(self):
        self.form_data['error_msg'] = 'This is an error'

        self.assertEqual(self.user.notification_set.count(), 0)
        res = self.client.post(self.url, self.form_data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(self.user.notification_set.count(), 1)

    def test_notifications_are_sent_only_once(self):
        self.form_data['error_msg'] = 'This is an error'

        self.assertEqual(self.user.notification_set.count(), 0)
        self.client.post(self.url, self.form_data)
        self.client.post(self.url, self.form_data)
        self.client.post(self.url, self.form_data)

        self.assertEqual(self.user.notification_set.count(), 1)

    def test_cancel_error_and_error_again(self):
        self.form_data['error_msg'] = 'This is an error'
        self.client.post(self.url, self.form_data)
        self.assertEqual(self.user.notification_set.count(), 1)

        self.form_data['error_msg'] = ''
        self.client.post(self.url, self.form_data)
        self.assertEqual(self.user.notification_set.count(), 1)

        self.form_data['error_msg'] = 'Another error'
        self.client.post(self.url, self.form_data)
        self.assertEqual(self.user.notification_set.count(), 2)
