from __future__ import absolute_import
__name__ = 'package_backends'

from main import settings

DEFAULT_BACKEND = 'portage'

try:
    backend = settings.PACKAGE_INFO_BACKEND
except AttributeError:
    backend = DEFAULT_BACKEND

#backend = __import__('package_backends.' + backend) 

#portage = backend.Portage()
