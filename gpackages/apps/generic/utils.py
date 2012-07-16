from __future__ import absolute_import, unicode_literals
from functools import partial
from inspect import getargspec
from django.core.cache import cache
from django.template.base import TagHelperNode, generic_tag_compiler, Template
from django.template.context import (Context, RequestContext,
    ContextPopException)

# Most part steeled from django code
def inclusion_cached_tag(file_name, register, cache_key_func, lang_code = True,
                        time_zone = True,
                        context_class=Context, takes_context=False, name=None):
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)

        class InclusionCachedNode(TagHelperNode):

            def render(self, context):
                resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
                key_kwargs = resolved_kwargs.copy()

                key = cache_key_func(*resolved_args, **resolved_kwargs)
                if lang_code:
                    lc = context.get('LANGUAGE_CODE')
                    lc = lc if lc else ''
                    key += lc
                if time_zone:
                    tz = context.get('TIME_ZONE')
                    tz = str(tz) if tz else ''
                    key += tz

                cache_v = cache.get(key)
                if cache_v is not None:
                    return cache_v
                _dict = func(*resolved_args, **resolved_kwargs)

                if not getattr(self, 'nodelist', False):
                    from django.template.loader import get_template, select_template
                    if isinstance(file_name, Template):
                        t = file_name
                    elif not isinstance(file_name, basestring) and is_iterable(file_name):
                        t = select_template(file_name)
                    else:
                        t = get_template(file_name)
                    self.nodelist = t.nodelist
                new_context = context_class(_dict, **{
                    'autoescape': context.autoescape,
                    'current_app': context.current_app,
                    'use_l10n': context.use_l10n,
                    'use_tz': context.use_tz,
                })
                # Copy across the CSRF token, if present, because
                # inclusion tags are often used for forms, and we need
                # instructions for using CSRF protection to be as simple
                # as possible.
                csrf_token = context.get('csrf_token', None)
                if csrf_token is not None:
                    new_context['csrf_token'] = csrf_token
                val = self.nodelist.render(new_context)
                cache.set(key, val)
                return val

        function_name = (name or
            getattr(func, '_decorated_function', func).__name__)
        compile_func = partial(generic_tag_compiler,
            params=params, varargs=varargs, varkw=varkw,
            defaults=defaults, name=function_name,
            takes_context=takes_context, node_class=InclusionCachedNode)
        compile_func.__doc__ = func.__doc__
        register.tag(function_name, compile_func)
        return func
    return dec
