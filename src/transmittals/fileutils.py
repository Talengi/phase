# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def trs_comments_file_path(revision, filename):
    return "transmittals/{key}_{revision}_trs_comments.{extension}".format(
        key=revision.document.document_key,
        revision=revision.revision_name,
        extension=filename.split('.')[-1]
    )
