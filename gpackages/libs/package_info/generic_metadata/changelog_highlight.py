from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

DATE_RE = r'\d\d [A-Z][a-z]{2} \d{4}'
EMAIL_RE = r'[\w\.\-]+@(?:\w+\.)+\w+'

# Literal.Date

class ChangelogLexer(RegexLexer):
    name = 'Changelog'
    aliases = ['changelog']
    filenames = ['Changelog']

    tokens = {
        'root': [
            (r'^# .*\n', Comment.Single), # Comment
            (r'^(\*)(.+)( )(\()(%s)(\))' % DATE_RE, bygroups(Operator, String, Name, Punctuation, Keyword, Punctuation)),
            #(r'^  ' , Whitespace, 'main'),
            (r'^(  )(%(date)s)(;)( +)([^<]*)(<)(%(email)s)(>)' % {'date': DATE_RE, 'email': EMAIL_RE},
                bygroups(Whitespace, Keyword, Punctuation, Whitespace, Name.Variable, Punctuation, Number, Number ), 'main'), # Date
            (EMAIL_RE, Number),
        ],
        'main': [
            (r' *\n\n', Punctuation, '#pop'),
            (DATE_RE, Keyword), # Date
            (EMAIL_RE, Number), # email
            (r'(,| |  )(\+[\w\.\-\+\/]+)', bygroups(Punctuation, Generic.Inserted)),
            (r'(,| |  )(\-[\w\.\-\+\/]+)', bygroups(Punctuation, Generic.Deleted)),
            (r'(,| |  )(\w[\w\.\-\+\/]+)', bygroups(Punctuation, Operator.Word)),
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
            (r'(?i)bug #\d+', String),
            (r'#\d+', String),
            (r'(?i)bug \d+', String),
            (r'\(|\)', Punctuation),
            (r'[^#\n ]+', Generic),
            (r' +', Whitespace),
        ]
    }
