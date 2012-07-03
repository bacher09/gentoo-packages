# Validators
from django.core.validators import URLValidator, validate_email 
from django.core.exceptions import ValidationError

validate_url = URLValidator()

__all__ = ('validate_email', 'validate_url', 'ValidationError')

REVISION_RE = r'r\d+'
VERSION_RE = r'[\w.]+'
NAME_RE = r'[\w+-]+'
