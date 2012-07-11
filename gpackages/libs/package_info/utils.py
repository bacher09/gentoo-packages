ciavc_author_template = 'http://cia.vc/stats/author/%s/'
def ciavc_link(name):
    return ciavc_author_template % name

def email_parse(email):
    e_l = email.split('@')
    if len(e_l) == 1:
        return (e_l[0], '')
    elif len(e_l) > 1:
        return (e_l[0], e_l[1])
    else:
        return ('','')
