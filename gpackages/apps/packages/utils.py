from package_info.generic import ToStrMixin

def gen_args(args):
    t = '%s=%s'
    l = (t % arg for arg in args)
    return '&'.join(l)

def get_link(host, script, args):
    return 'http://%(host)s/%(script)s?%(args)' % {'host': host,
                                                   'script': script,
                                                   'args': get_args(args)}

