def revision_file_path(revision, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision.

    """
    has_status = bool(getattr(revision, 'status', None))
    return "revisions/{key}_{revision}{status}.{extension}".format(
        key=revision.document.document_key,
        revision=revision.name,
        extension=filename.split('.')[-1],
        status="_" + revision.status if has_status else ''
    )
