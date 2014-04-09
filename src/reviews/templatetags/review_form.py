from django import template


register = template.Library()


@register.simple_tag
def file_link(file):
    if file:
        link = '<a href="%s">%s</a>' % (file.url, file)
    else:
        link = ''
    return link
