from __future__ import absolute_import
__name__ = 'package_info.package_backends'

DEFAULT_BACKEND = 'portage'

def import_backend(backend):
    backend_module = __import__(__name__, fromlist=[backend], level = 0) 
    return backend_module

def get_backend_name():
    backend = DEFAULT_BACKEND
    try:
        from main import settings
    except ImportError:
        # should log this
        pass
    else:
        try:
            backend = settings.PACKAGE_INFO_BACKEND
        except AttributeError:
            pass
    return backend

def load_backend(backend):
    try:
        backend_module = import_backend(backend)
    except ImportError:
        try:
            backend_module = import_backend(DEFAULT_BACKEND)
        except ImportError:
            raise

    backend_module = getattr(backend_module, backend)

    portage = backend_module.Portage()
    return portage

def get_backend():
    backend = get_backend_name()
    return load_backend(backend)
