# Validators
from django.core.validators import URLValidator, validate_email, RegexValidator
from django.core.exceptions import ValidationError

validate_url = URLValidator()

__all__ = ('validate_email', 'validate_url', 'ValidationError')

REVISION_RE = r'r\d+'
VERSION_RE = r'\d[\w\.]*'
NAME_RE = r'[\w+-]+?'

validate_revision = RegexValidator('^%s$' % REVISION_RE)
validate_version = RegexValidator('^%s$' % VERSION_RE)
validate_name = RegexValidator('^%s$' % NAME_RE)
