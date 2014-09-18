def review_comments_file_path(review, filename):
    """Rename document files on upload to match a custom filename."""
    from reviews.models.Review import ROLES

    role_part = {
        ROLES.reviewer: review.reviewer_id,
        ROLES.leader: 'leader',
        ROLES.approver: 'GTG',
    }

    return "{key}_{revision}_{role}_comments.{extension}".format(
        key=review.document.document_key,
        revision=review.revision,
        role=role_part[review.role],
        extension=filename.split('.')[-1]
    )
