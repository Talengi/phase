# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from distriblists.models import DistributionList
from categories.models import Category


class DistributionListImportForm(forms.Form):
    required_css_class = 'required'

    category = forms.ModelChoiceField(
        label=_('Category'),
        queryset=Category.objects.all(),
    )
    xls_file = forms.FileField(
        label=_('Select your file'),
        help_text=_('It must be in xls or xlsx format'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        categories = kwargs.pop('categories')
        super(DistributionListImportForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = categories


class DistributionListExportForm(forms.Form):
    required_css_class = 'required'

    category = forms.ModelChoiceField(
        label=_('Category'),
        queryset=Category.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        categories = kwargs.pop('categories')
        super(DistributionListExportForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = categories


class DistributionListValidationMixin(object):
    """Common code for validating forms with distrib lists."""
    def clean(self):
        data = super(DistributionListValidationMixin, self).clean()

        # Check that no user appears twice in the distrib list
        distrib_list = []

        leader = data.get('leader', None)
        if leader:
            distrib_list.append(leader)

        approver = data.get('approver', None)
        if approver:
            distrib_list.append(approver)

        reviewers = data.get('reviewers', [])
        distrib_list += reviewers

        distrib_set = set(distrib_list)
        if len(distrib_list) != len(distrib_set):
            msg = _('The same user cannot appear multiple times in the same '
                    'distribution list.')
            raise ValidationError(msg, code='duplicate_distrib_list')

        return data


class DistributionListForm(DistributionListValidationMixin, forms.ModelForm):
    class Meta:
        model = DistributionList
        exclude = []

    def __init__(self, *args, **kwargs):
        super(DistributionListForm, self).__init__(*args, **kwargs)
        self.fields['leader'].error_messages = {
            'required': _('You must define a leader'),
        }

    def clean_leader(self):
        """Leader must be a member of all selected categories."""
        leader = self.cleaned_data['leader']
        self.validate_user_categories(leader)
        return leader

    def clean_approver(self):
        """Approver must be a member of all selected categories."""
        approver = self.cleaned_data['approver']
        if approver:
            self.validate_user_categories(approver)
        return approver

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']
        errors = []
        for reviewer in reviewers:
            try:
                self.validate_user_categories(reviewer)
            except ValidationError, e:
                errors.append(e.message)

        if len(errors) > 0:
            raise ValidationError(errors)

        return reviewers

    def validate_user_categories(self, user):
        """Check that user belongs to the selected categories."""
        if 'categories' not in self.cleaned_data:
            return

        user_categories = set(user.categories.all())
        categories = set(self.cleaned_data['categories'])

        if not categories.issubset(user_categories):
            diff = categories - user_categories
            formatted_diff = ', '.join(d.__unicode__() for d in diff)
            msg = _('The user "{}" must be a member of all the selected '
                    'categories. The following categories are missing: '
                    '{}'.format(user.name, formatted_diff))
            raise ValidationError(msg)
