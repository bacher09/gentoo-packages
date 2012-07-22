from pygments.lexer import RegexLexer, bygroups
from pygments.formatters import HtmlFormatter
from pygments.formatters.html import _escape_html_table
from pygments.style import Style
from pygments.token import *
import re

DATE_RE = r'\d\d [A-Z][a-z]{2} \d{4}'
EMAIL_RE = r'[\w\.\-]+@(?:\w+\.)+\w+'

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

class ChangelogLexer(RegexLexer):
    name = 'Changelog'
    aliases = ['changelog']
    filenames = ['Changelog']

    tokens = {
        'root': [
            (r'^# .*\n', Comment.Single), # Comment
            (r'^(\*)(.+)( )(\()(%s)(\))' % DATE_RE, bygroups(Operator, PackageName, Whitespace, Punctuation, Date, Punctuation)),
            #(r'^  ' , Whitespace, 'main'),
            (r'^(  )(%(date)s)(;)( +)([^<]*)(<)(%(email)s)(>)' % {'date': DATE_RE, 'email': EMAIL_RE},
                bygroups(Whitespace, Date, Punctuation, Whitespace, AuthorName, Punctuation, Number, Punctuation), 'main'), # Date
            (EMAIL_RE, Email),
        ],
        'main': [
            (r' *\n\n', Punctuation, '#pop'),
            (EMAIL_RE, Email), 
            (r'(,| |  )(\+[\w\.\-\+\/]+)', bygroups(Punctuation, FilePlus)),
            (r'(,| |  )(\-[\w\.\-\+\/]+)', bygroups(Punctuation, FileMinus)),
            (r'(,| |  )(\w[\w\.\-\+\/]+)', bygroups(Punctuation, File)),
            (r':( +|\n)', Punctuation, 'message'),
            (r';|<|>|,', Punctuation),
            (r' |\n', Whitespace),
        ],
        'message': [
            (r' *\n', Punctuation, '#pop:2'),
            #(r'#\d+', String),
            (r'  ', Whitespace, 'message_text'),
        ],
        'message_text': [
            (r' *\n', Whitespace, '#pop'),
            (r'(?i)bug #\d+', Bug),
            (r'#\d+', Bug),
            (r'(?i)bug \d+', Bug),
            (r'\(|\)|<|>', Punctuation),
            (EMAIL_RE, Email), 
            #(KEYWORD_RE, Name.Variable),
            (r'[^#\n ]+', Generic),
            (r' +', Whitespace),
        ]
    }

class ChangelogHtmlFormater(HtmlFormatter):
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
        return value

class ChangelogStyle(Style):
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
    }
