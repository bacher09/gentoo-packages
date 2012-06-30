from django import template
register = template.Library()


class MyPage(object):
    __slots__ = ('num', 'is_active')

    def __init__(self, num, current):
        self.num = num
        if num == current:
            self.is_active = True
        else:
            self.is_active = False

    def active(self):
        return 'active' if self.is_active else ''

    def link(self):
        return '?page=%s' % self.num

def get_middle_range(current, page_num, num):
    start = (current - num) if current > num else 1
    end = (current + num) 
    if end > page_num:
        end = page_num

    return start, end

def get_pages_in_range(start, end, current):
    return (MyPage(n, current) for n in range(start, end+1))

def get_l_ragne(m_start, num):
    if m_start <= 1:
        return 1, 0, False

    l_end = num
    l_gap = True
    if l_end >= m_start:
        l_end = m_start - 1

    if l_end + 1 >= m_start:
        l_gap = False

    return 1, l_end, l_gap

def get_r_range(m_end, num_pages, num):
    if m_end >= num_pages:
        return num_pages, 0, False

    r_start = num_pages - num + 1
    r_gap = True
    if r_start <= m_end:
        r_start = m_end + 1

    if r_start -1 <= m_end:
        r_gap = False

    return r_start, num_pages, r_gap

@register.inclusion_tag('paginator.html')
def paginator(page, num_middle, num_first, n_a_p = True, all_num = 0):
    paginator = page.paginator
    num_pages = paginator.num_pages
    is_paginated = True if num_pages > 1 else False
    if all_num >= num_pages:
        m_start, m_end = 1, num_pages
        first, last = (), ()
        l_gap, r_gap = False, False
    else:
        m_start, m_end = get_middle_range(page.number, num_pages, num_middle)
        l_start, l_end, l_gap = get_l_ragne(m_start, num_first)
        r_start, r_end, r_gap = get_r_range(m_end, num_pages, num_first)
        first = get_pages_in_range(l_start, l_end, page.number)
        last = get_pages_in_range(r_start, r_end, page.number)
    middle = get_pages_in_range(m_start, m_end, page.number)

    return {'page_obj': page,
            'is_paginated': is_paginated,
            'paginator': paginator,
            'middle_pages': middle,
            'first_pages': first,
            'last_pages': last,
            'left_gap': l_gap,
            'right_gap': r_gap,
            'next_and_prev': bool(n_a_p)}
