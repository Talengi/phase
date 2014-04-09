def reviewers_comments_file_path(review, filename):
    """Rename document files on upload to match a custom filename."""
    return "{key}_{revision}_{reviewer}_comments.{extension}".format(
        key=review.document.document_key,
        revision=review.revision,
        reviewer=review.reviewer_id,
        extension=filename.split('.')[-1]
    )
