import re
from ..generic import ToStrMixin, toint
from ..parse_cp import VERSIONS_RE_P, EbuildRevMixin
from ..validators import NAME_RE
from datetime import datetime, date, MINYEAR
import calendar
from difflib import get_close_matches

DATE_FORMAT = '%d %b %Y'

CHANGELOG_DATE_RE_P = r"(?P<date>(?P<day>\d\d) " \
                      r"(?P<month>[A-Z][a-z]{2}) (?P<year>\d{4}))"

CHANGELOG_MESSAGE_RE_STR = r"^\s+%(date)s; " \
                           r"(?:(?P<name>[^\<]+) )?\<(?P<email>[\w\@\.\-]+)\>" \
                           r"(?P<files>.*):(?P<message>.*)$" % {
                                'date' : CHANGELOG_DATE_RE_P
                            }

FULL_NAME_RE_STR = r"(?P<name>%(name)s)%(versions)s" % {
                        'name' : NAME_RE,
                        'versions' : VERSIONS_RE_P
                    }

CHANGELOG_VERSION_RE_STR = "^\*%(name)s \(%(date)s\)$" % {
                                'name' : FULL_NAME_RE_STR,
                                'date' : CHANGELOG_DATE_RE_P
                            }
changelog_m_re = re.compile(CHANGELOG_MESSAGE_RE_STR, re.S)
changelog_v_re = re.compile(CHANGELOG_VERSION_RE_STR)
clear_re = re.compile(r'\s+')
email_re = re.compile(r'(?P<email_name>[\w\.\-]+)@(?P<email_host>[\w\.\-]+)')
date_re = re.compile(CHANGELOG_DATE_RE_P)

MONTH_TUPLE = tuple(calendar.month_abbr)[1:]

def parse_date(date_str, traceback = False):
    try:
        mdate = datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        if traceback:
            raise
        # Bad date format, humman error
        # Add here logger
        mdate = date.min
        m = date_re.match(date_str)
        if m is not None:
            dct = m.groupdict()
            day = dct['day']
            month = dct['month']
            year = dct['year']
            if month not in MONTH_TUPLE:
                months = get_close_matches(month, MONTH_TUPLE, 1)
                if len(months) >=1:
                    month = months[0]
                else:
                    month = MONTH_TUPLE[0]

            month_num = MONTH_TUPLE.index(month) + 1
            year_num = toint(year, MINYEAR)
            day_num = toint(day, 1)
            try:
                mdate = date(year_num, month_num, day_num)
            except ValueError:
                mdate = date.min

    return mdate

    return mdate.date()

def date_str(date):
    return date.strftime(DATE_FORMAT)

def clear_spaces(text):
    return clear_re.sub(' ', text)

class ChangeLogVersion(ToStrMixin, EbuildRevMixin):

    __slots__ = ('date', 'name', 'version', 'revision', '_cache')

    def __init__(self, version_dict):
        self.date = parse_date(version_dict['date'])
        self.name = version_dict['name']
        self.version = version_dict['version']
        self.revision = version_dict['revision']

    @property
    def fullversion(self):
        prefix = '-' + self.revision if self.revision else ''
        return '%s%s' % (self.version, prefix)

    @property
    def fullname(self):
        return '%s-%s' % (self.name, self.fullversion)

    @property
    def date_str(self):
        return date_str(self.date)
    
    def __unicode__(self):
        return '%s (%s)' % (self.fullname, self.date_str)

class ChangeLogMessage(ToStrMixin):

    def __init__(self, message_dict):
        self.date = parse_date(message_dict['date'])
        self.email = message_dict['email'].strip()
        name = message_dict['name']
        if name:
            name = name.decode('utf-8')
            self.name = name.strip()
        else:
            self.name = None
        self.files = map(lambda x: x.strip(), message_dict['files'].split(','))
        self.message = clear_spaces(message_dict['message'])

    @property
    def date_str(self):
        return date_str(self.date)

    @property
    def fullname(self):
        name = self.name + ' ' if self.name else ''
        return '%s<%s>' % (name, self.email)

    @property
    def header(self):
        return '%s; %s' % (self.date_str, self.fullname)
    
    def __unicode__(self):
        return self.header

def parse_changelog(changelog):
    if not changelog:
        raise StopIteration
    lst = changelog.split("\n\n")
    for item in lst:
        if item.startswith('*'):
            for sitem in item.split('\n'):
                v = changelog_v_re.match(item)
                if v is not None:
                    yield ('version', v.groupdict())
            continue
        m = changelog_m_re.match(item)
        if m is not None:
            yield ('message', m.groupdict())
        else:
            yield ('comment', item)

class ChangeLog(ToStrMixin):

    def __init__(self, changelog_text):
        self.items = []
        for t, v in parse_changelog(changelog_text):
            if t == 'version':
                v = ChangeLogVersion(v)
            elif t == 'message':
                v = ChangeLogMessage(v)

            self.items.append(v)

    def __unicode__(self):
        return 'changelog'
