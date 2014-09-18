def review_comments_file_path(review, filename):
    """Rename document files on upload to match a custom filename."""
    from reviews.models import Review

    role_part = {
        Review.ROLES.reviewer: review.reviewer_id,
        Review.ROLES.leader: 'leader',
        Review.ROLES.approver: 'GTG',
    }

    return "{key}_{revision}_{role}_comments.{extension}".format(
        key=review.document.document_key,
        revision=review.revision_name,
        role=role_part[review.role],
        extension=filename.split('.')[-1]
    )
