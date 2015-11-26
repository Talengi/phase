# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def trs_comments_file_path(revision, filename):
    return "reviews/{key}_{revision}_comments.{extension}".format(
        key=revision.document.document_key,
        revision=revision.revision_name,
        extension=filename.split('.')[-1]
    )
