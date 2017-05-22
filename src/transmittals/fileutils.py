# -*- coding: utf-8 -*-



def file_transmitted_file_path(revision, filename):
    return "transmittals/{key}_{revision}_file_transmitted.{extension}".format(
        key=revision.document.document_key,
        revision=revision.revision_name,
        extension=filename.split('.')[-1]
    )


# Kept for migrations compatibility purpose
def trs_comments_file_path(revision, filename):
    return "transmittals/{key}_{revision}_file_transmitted.{extension}".format(
        key=revision.document.document_key,
        revision=revision.revision_name,
        extension=filename.split('.')[-1]
    )
