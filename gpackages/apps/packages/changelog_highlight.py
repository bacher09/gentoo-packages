from package_info.generic_metadata.changelog_highlight import  Email, \
    ChangelogHtmlFormater, ChangelogLexer, ChangelogStyle, highlight

from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch

def maintainer_link_by_email(email):
    from . import models
    try:
        obj = models.MaintainerModel.objects.get(email = email)
        url = reverse('packages', kwargs = {'maintainer' : obj.pk})
    except (models.MaintainerModel.DoesNotExist, NoReverseMatch):
        return None
    else:
        return url
    

class ChangelogHtmlFormaterWithLinks(ChangelogHtmlFormater):

    def __init__(self, *args, **kwargs):
        super(ChangelogHtmlFormaterWithLinks, self).__init__(*args, **kwargs)
        self._maintainer_url = {}

    def token_decorate(self, token, value):
        if token == Email:
            if value in self._maintainer_url:
                return self._maintainer_url[value]
            url = maintainer_link_by_email(value)
            if url is not None:
                name, domain = value.split('@')
                nvalue = '<a href="{1}" class="defcolor">{0}</a>'. \
                    format(name, url)
                self._maintainer_url[value] = nvalue
                return nvalue

        value = super(ChangelogHtmlFormaterWithLinks, self). \
            token_decorate(token, value)
        return value

def changelog_highlight(text):
    "Shortcut for generating highlighted changelog html output"
    return highlight(text, ChangelogLexer(), 
                     ChangelogHtmlFormaterWithLinks(style = ChangelogStyle))
