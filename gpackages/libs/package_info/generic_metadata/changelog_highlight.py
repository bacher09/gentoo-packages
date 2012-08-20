from pygments.lexer import RegexLexer, bygroups, include
from pygments.formatters import HtmlFormatter, Terminal256Formatter
from pygments.formatters.html import _escape_html_table
from pygments.style import Style
from pygments.token import *
from pygments import highlight
import re
from collections import deque
from ..utils import ciavc_link

DATE_RE = r'\d\d? [A-Z][a-z]{2} \d{4}'
EMAIL_RE = r'[\w\.\-\+]+@(?:[\w\-]+\.)+\w+'
LINK_RE = r'https?:\/\/(?:[\w\-]+\.)+\w+(:?\/[\w\/\.\-\_\+\&\%\?#=]+)?'
BUG_NUM_RE =  r'(\d+)'
bugnum_re = re.compile(BUG_NUM_RE)

ARCHES = [ u'alpha', u'amd64', u'amd64-fbsd', u'amd64-linux', u'arm',
           u'arm-linux', u'hppa', u'hppa-hpux', u'ia64', u'ia64-hpux',
           u'ia64-linux', u'm68k', u'm68k-mint', u'mips', u'ppc', u'ppc-aix',
           u'ppc-macos', u'ppc-openbsd', u'ppc64', u's390', u'sh', u'sparc',
           u'sparc-fbsd', u'sparc-solaris', u'sparc64-solaris', u'x64-freebsd',
           u'x64-macos', u'x64-openbsd', u'x64-solaris', u'x86', u'x86-fbsd',
           u'x86-freebsd', u'x86-interix', u'x86-linux', u'x86-macos',
           u'x86-netbsd', u'x86-openbsd', u'x86-solaris', u'x86-winnt' ]

KEYWORD_RE = r'[-~]?(?:%s)' % '|'.join(map(re.escape, ARCHES))

# Literal.Date

Date = Literal.Date
PackageName = Name.Namespace
FilePlus = Generic.Inserted
FileMinus = Generic.Deleted
File = Operator.Word
Email = Number
AuthorName = Name.Variable
Bug = String
Link = Keyword

class ChangelogLexer(RegexLexer):
    "Pygments changelog lexer"

    name = 'Changelog'
    aliases = ['changelog']
    filenames = ['Changelog']

    tokens = {
        'root': [
            (r'^# .*\n', Comment.Single), # Comment
            (r'^(\*)(.+)( )(\()(%s)(\))' % DATE_RE, bygroups(Operator, PackageName, Whitespace, Punctuation, Date, Punctuation)),
            (r'^(  )(%(date)s)(;)( +)([^<]*)(<)(%(email)s)(>)' % {'date': DATE_RE, 'email': EMAIL_RE},
                bygroups(Whitespace, Date, Punctuation, Whitespace, AuthorName, Punctuation, Number, Punctuation), 'main'), # Date
            include('email'),
            (r' ', Whitespace),
            include('bugs'),
            (r'\(|\)|<|>', Punctuation),
            include('email'),
            include('link'),
            #(KEYWORD_RE, Name.Variable),
            (r'[^#\n ]+', Generic),
            (r' +', Whitespace),
        ],
        'main': [
            (r' *\n\n', Punctuation, '#pop'),
            (EMAIL_RE, Email), 
            (r'(,| |  )(\+[\w\.\-\+\/]+)', bygroups(Punctuation, FilePlus)),
            (r'(,| |  )(\-[\w\.\-\+\/]+)', bygroups(Punctuation, FileMinus)),
            (r'(,| |  )([\w\*][\w\.\-\+\/]+)', bygroups(Punctuation, File)),
            (r': *\n *\n|:(?: +|\n)|: +', Punctuation, 'message'),
            (r';|<|>|,', Punctuation),
            include('link'),
            (r' |\n', Whitespace),
        ],
        'message': [
            (r' *\n', Punctuation, '#pop:2'),
            #(r'#\d+', String),
            (r'  ', Whitespace, 'message_text'),
        ],
        'message_text': [
            (r' *\n', Whitespace, '#pop'),
            include('bugs'),
            include('email'),
            include('link'),
            #(KEYWORD_RE, Name.Variable),
            (r' +', Whitespace),
            (r'.', Generic),
        ],
        'bugs' : [
            (r'(?i)bug #\d+', Bug),
            (r'#\d+', Bug),
            (r'(?i)bug \d+', Bug),
        ],
        'email': [
            (EMAIL_RE, Email), 
        ],
        'link': [
            (LINK_RE, Link),
        ]
    }

class ChangelogHtmlFormater(HtmlFormatter):
    "Pygments html changelog formater"

    def _format_lines(self, tokensource):
        """
        Copyed from pygments source litle modified.
        """
        nocls = self.noclasses
        lsep = self.lineseparator
        # for <span style=""> lookup only
        getcls = self.ttype2class.get
        c2s = self.class2style
        escape_table = _escape_html_table

        lspan = ''
        line = ''
        for ttype, value in tokensource:
            if nocls:
                cclass = getcls(ttype)
                while cclass is None:
                    ttype = ttype.parent
                    cclass = getcls(ttype)
                cspan = cclass and '<span style="%s">' % c2s[cclass][0] or ''
            else:
                cls = self._get_css_class(ttype)
                cspan = cls and '<span class="%s">' % cls or ''

            parts = value.translate(escape_table).split('\n')

            # for all but the last line
            for part in parts[:-1]:
                part = self.token_decorate(ttype, part)
                if line:
                    if lspan != cspan:
                        line += (lspan and '</span>') + cspan + part + \
                                (cspan and '</span>') + lsep
                    else: # both are the same
                        line += part + (lspan and '</span>') + lsep
                    yield 1, line
                    line = ''
                elif part:
                    yield 1, cspan + part + (cspan and '</span>') + lsep
                else:
                    yield 1, lsep
            # for the last line
            last = self.token_decorate(ttype, parts[-1])
            if line and last:
                if lspan != cspan:

                    line += (lspan and '</span>') + cspan + last
                    lspan = cspan
                else:
                    line += last 
            elif last:
                line = cspan + last
                lspan = cspan
            # else we neither have to open a new span nor set lspan

        if line:
            yield 1, line + (lspan and '</span>') + lsep

    def token_decorate(self, token, value):
        if token == Link:
            value = '<a href="{0}" rel="nofollow">{0}</a>'.format(value)
        elif token == Bug:
            num_m = bugnum_re.search(value)
            bugs_url_template = "https://bugs.gentoo.org/{0}"
            if num_m is not None:
                num = num_m.group()
                link = bugs_url_template.format(num)
                value = '<a href="{1}" class="defcolor">{0}</a>'. \
                    format(value, link)
        elif token == Email:
            name, domain = value.split('@')
            value = '<a href="{1}" class="defcolor">{0}</a>'. \
                format(name, ciavc_link(name))
        return value

class ChangelogStyle(Style):
    "Pygments style for gentoo changelog"

    default_style = ""
    styles = {
        Comment:                'italic #888',
        Date:                   '#F90',
        FilePlus:               'bold #0F0',
        FileMinus:              'bold #F00',
        File:                   'bold #C0A',
        PackageName:            'bold',
        Bug:                    '#E00',
        Email:                  '#0CF',
        AuthorName:             'bold #1C9',
        #Error:                  'bold underline #F00',
    }

def changelog_highlight(text):
    "Shortcut for generating highlighted changelog html output"
    return highlight(text, ChangelogLexer(), 
                     ChangelogHtmlFormater(style = ChangelogStyle))

def changelog_termial_highlight(text):
    """Shortcut for generating highlighted terminal changelog  output
    Used for debuging lexer """
    return highlight(text, ChangelogLexer(), 
                     Terminal256Formatter(style = ChangelogStyle))

def changelog_style_css():
    "Shortcut for generating css style for pygments `ChangelogStyle`"
    f = ChangelogHtmlFormater(style = ChangelogStyle)
    return f.get_style_defs()

def group_tokens(text):
    """Combine tokens to groups.

    Args:
        text -- changelog text

    Yields:
        (group_type, group), where group_type are: `None`, `'version'` or \
        `'message'`
        group are array of tuples (toke, value)

    """
    c = ChangelogLexer()
    queue = deque()
    group_type = None 
    group = []
    for token, value in c.get_tokens(text):
        queue.append((token, value))

        if len(queue)>6:
            token_q, value_q = queue[0]
            if token_q == Operator and value_q == '*':
                yield (group_type, group)
                group_type = 'version'
                group = []
            elif token_q == Whitespace:
                token2_q, value2_q = queue[1]
                if token2_q == Date:
                    token3_q, value3_q = queue[2]
                    if token3_q == Punctuation:
                        yield (group_type, group)
                        group_type = 'message'
                        group = []

            group.append(queue.popleft())

    yield (group_type, group + list(queue))

def latest_message_group(text):
    """Args:
        text - changelog text
    Returns: return latest message group"""
    for group_type, group in group_tokens(text):
        if group_type == 'message':
            return group

def latest_group_messages_group(text):
    groups = []
    for group_type, group in group_tokens(text):
        if group_type == 'version':
            groups.append((group_type, group))
        if group_type == 'message':
            groups.append((group_type, group))
            return groups

def tokensgroup_to_toknes(groups):
    tk = []
    for group_type, group in groups:
        tk += group
    return tk

def tokens_to_text(lex):
    "Convert tokenized input to text"
    mystr = ''
    for token, value in lex:
        mystr += value
    return mystr

def latest_message(text):
    "Return latest message text"
    return tokens_to_text(latest_message_group(text))

def latest_group_messages(text):
    "Returns latest messages like it done on packages.gentoo.org"
    groups = latest_group_messages_group(text)
    return tokens_to_text(tokensgroup_to_toknes(groups))

