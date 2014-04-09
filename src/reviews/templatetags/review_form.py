from django import template


register = template.Library()


def icon(name):
    return '<span class="glyphicon glyphicon-%s"></span>' % name


def icons(names):
    return ' '.join(icon(name) for name in names)


@register.simple_tag
def yesno(value):
    name = 'ok' if value else 'remove'
    return icon(name)


@register.simple_tag
def review_leader_icons(revision):
    names = []
    if revision.leader_step_closed:
        names.append('ok')
    else:
        names.append('remove')

    if revision.leader_comments:
        names.append('comment')

    return icons(names)


@register.simple_tag
def review_approver_icons(revision):
    names = []
    if revision.review_end_date:
        names.append('ok')
    else:
        names.append('remove')

    if revision.approver_comments:
        names.append('comment')

    return icons(names)
