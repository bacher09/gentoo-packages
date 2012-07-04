import os
import os.path
import re
import hashlib
from datetime import datetime
from email import message_from_string
from email.utils import getaddresses
from ..generic import ToStrMixin, toint, file_get_content
from ..abstract import AbstractNewsItem, SimpleMaintainer

NEWS_STR_RE = r'^(?P<date>\d{4,4}-\d{2}-\d{2})-(?P<title>.*)$'
news_re = re.compile(NEWS_STR_RE)

class News(ToStrMixin):
    
    def __init__(self, repo_path = '/usr/portage'):
        self.news_path = os.path.join(repo_path, 'metadata', 'news')
        if not os.path.isdir(self.news_path):
            raise ValueError
        # For repr
        self.repo_path = repo_path 

    def iter_news(self):
        for name in os.listdir(self.news_path):
            try:
                i = NewsItem(self.news_path, name)
            except ValueError:
                pass
            else:
                yield i

    def __iter__(self):
        return self.iter_news()

    def __unicode__(self):
        return unicode(self.repo_path)

class NewsItem(ToStrMixin):

    N_ITEM_P = r'^%(name)s\.(?P<lang>[a-z]{2})\.txt$'

    def __init__(self, news_path, news_dir):
        ndir = os.path.join(news_path, news_dir)
        if not os.path.isdir(ndir):
            raise ValueError
        m = news_re.match(news_dir)
        if m is None:
            raise ValueError
        p_dct =  m.groupdict()
        try:
            date = datetime.strptime(p_dct['date'], '%Y-%m-%d')
        except ValueError:
            raise
        else:
            self.date = date.date()

        self.title = p_dct['title']
        self.name = news_dir
        self.news_dir = ndir
        self._news_dict = {}
        self._fetch_news()

    def _iter_news_items(self):
        pattern_str = self.N_ITEM_P % {'name': re.escape(self.name)}
        pattern = re.compile(pattern_str)
        for item in os.listdir(self.news_dir):
            m = pattern.match(item)
            full_path = os.path.join(self.news_dir, item)
            if m is not None and os.path.isfile(full_path):
                lang = m.groupdict()['lang']
                yield (full_path, lang)
            
    def _fetch_news(self):
        for item, lang in self._iter_news_items():
            self._news_dict[lang] = NewsItemLang(item,
                                                 self.date,
                                                 lang,
                                                 self.title)

    @property
    def default_news(self):
        return self._news_dict['en']

    @property
    def news(self):
        return self._news_dict

    def __unicode__(self):
        return unicode(self.name)

def maintainers_list(tuple_list):
    s = set()
    if tuple_list:
        for name, email in getaddresses(tuple_list):
            s.add(SimpleMaintainer(email, name))
    return tuple(s)

class NewsItemLang(AbstractNewsItem):
    
    def __init__(self, item, date, lang = 'en', name = ''):
        f = file_get_content(item)
        self.sha1 = hashlib.sha1(f).hexdigest()
        self._mes_obj = message_from_string(f)
        self.date = date
        self.lang = lang
        self.name = name

    @property
    def title(self):
        return self._mes_obj.get('Title')

    @property
    def revision(self):
        return toint(self._mes_obj.get('Revision', 1),1)

    @property
    def format_ver(self):
        g = self._mes_obj.get('News-Item-Format', '1.0')
        try:
            maj, min = g.split('.')
        except ValueError:
            maj, min = 1, 0

        return toint(maj,1), toint(min, 0)

    @property
    def authors(self):
        return maintainers_list(self._mes_obj.get_all('Author'))

    @property
    def translators(self):
        return maintainers_list(self._mes_obj.get_all('Translator'))

    @property
    def message(self):
        return self._mes_obj.get_payload()

