"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import models
from django.test.client import RequestFactory
from django.http import Http404
from operator import attrgetter
from time import sleep
from . import views
import re

class Tag(models.Model):
    name = models.CharField(unique = True, max_length = 40)

    def __unicode__(self):
        return self.name

class Messages(models.Model):
    title = models.CharField(max_length = 120)
    text = models.TextField()
    published = models.BooleanField(default = False)
    created_datetime = models.DateTimeField(auto_now_add = True)
    updated_datetime = models.DateTimeField(auto_now = True)
    tags = models.ManyToManyField(Tag, blank = True)

    def __unicode__(self):
        return self.title

class TestingViewMixin(object):
    
    def init_test_args(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def get_queryset(self):
        return self.queryset

    def get_context_data(self, **kwargs):
        dct = kwargs.copy()
        return dct

class MessagesFilter(views.MultipleFilterListViewMixin, TestingViewMixin):
    queryset = Messages.objects.all()
    m2m_filter = set(['tags'])
    allowed_many = {'tags': 3 }
    boolean_filters = ('published',)
    allowed_filter = { 'title':'title',
                       'published' : 'published',
                       'tags' : 'tags__name' }

    allowed_order = { 'create': 'created_datetime',
                      'update': 'updated_datetime', 
                       None   : 'created_datetime' }

    def init_test(self, request):
        url_re = re.compile(r'^%s$' % self.get_url_part())
        m = url_re.match(request.path[1:])
        if m is None:
            raise Http404('Bad url')
        kwargs = m.groupdict()
        self.init_test_args(request, **kwargs)

    def __init__(self, request):
        self.init_test(request)


class SimpleTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        tags = []
        for tag in ['one', 'two', 'three', 'four', 'five', 'six', 'seven']:
            tag_obj = Tag.objects.create(name = tag)
            tags.append(tag_obj)

        m_obj = Messages.objects.create(title = 'First message',
                                        text = 'Message',
                                        published = True)
        m_obj.tags.add(*tags[:2])

        m_obj = Messages.objects.create(title = 'Second message',
                                        text = 'Message',
                                        published = False)
        m_obj.tags.add(*tags[2:4])

        mu_obj = Messages.objects.create(title = 'Update',
                                         text = 'Message',
                                         published = False)
        mu_obj.tags.add(*tags[4:])

        m_obj = Messages.objects.create(title = 'New',
                                        text = 'Message',
                                        published = True)
        m_obj.tags.add(tags[0], tags[6])

        m_obj = Messages.objects.create(title = 'title',
                                        text = 'Message',
                                        published = False)
        m_obj.tags.add(tags[3], tags[5])

        m_obj = Messages.objects.create(title = 'message',
                                        text = 'Message',
                                        published = True)
        m_obj.tags.add(tags[6])

        m_obj = Messages.objects.create(title = 'cats',
                                        text = 'Message',
                                        published = True)
        m_obj.tags.add(tags[5])
        m_obj = Messages.objects.create(title = 'dogs',
                                        text = 'Message',
                                        published = False)
        m_obj.tags.add(tags[5])

        # For changed updated_datetime
        sleep(3)
        mu_obj.text = 'Updated'
        mu_obj.save()

    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)

    def test_filtering_view_url(self):
        url = MessagesFilter.get_url_part()
        self.assertEqual(url, '(?:published/(?P<published>yes|no)/)?' \
                              '(?:tags/(?P<tags>[^/]+)/)?' \
                              '(?:title/(?P<title>[^/]+)/)?' \
                              '(?:order/(?P<order>[a-z]*)/)?(?P<rev>rev/)?')

    def test_filtering_view_query_boolean(self):
        active = [
             "First message",
             "New",
             "message",
             "cats"
        ]
        inactive = [
             "Second message",
             "Update",
             "title",
             "dogs"
        ]
        request = self.factory.get('/published/yes/')
        self.assertQuerysetEqual(
            MessagesFilter(request).get_queryset(), 
            active, 
            attrgetter("title")
        )

        request = self.factory.get('/published/no/')
        self.assertQuerysetEqual(
            MessagesFilter(request).get_queryset(), 
            inactive, 
            attrgetter("title")
        )
        request = self.factory.get('/?published=yes')
        self.assertQuerysetEqual(
            MessagesFilter(request).get_queryset(), 
            active, 
            attrgetter("title")
        )

        request = self.factory.get('/?published=no')
        self.assertQuerysetEqual(
            MessagesFilter(request).get_queryset(), 
            inactive, 
            attrgetter("title")
        )

    def test_filtering_view_query_ordering(self):
        request = self.factory.get('/order/update/rev/')
        first = MessagesFilter(request).get_queryset()[0]
        self.assertEqual(first.title, "Update")

        request = self.factory.get('/order/test/')
        with self.assertRaises(Http404):
            MessagesFilter(request).get_queryset()

        request = self.factory.get('/order/newtest/rev/')
        with self.assertRaises(Http404):
            MessagesFilter(request).get_queryset()

        request = self.factory.get('/?order=update&rev=1')
        first = MessagesFilter(request).get_queryset()[0]
        self.assertEqual(first.title, "Update")

        request = self.factory.get('/?order=test')
        with self.assertRaises(Http404):
            MessagesFilter(request).get_queryset()

        request = self.factory.get('/?order=newtest&rev=1')
        with self.assertRaises(Http404):
            MessagesFilter(request).get_queryset()

    def test_filtering_view_query_search(self):
        def title_test(title):
            request = self.factory.get('/title/%s/' % title)
            obj = MessagesFilter(request).get_queryset()[0]
            self.assertEqual(obj.title, title)

        title_test("title")
        title_test("cats")
        title_test("dogs")
        title_test("New")

        def title_test2(title):
            request = self.factory.get('/?title=%s' % title)
            obj = MessagesFilter(request).get_queryset()[0]
            self.assertEqual(obj.title, title)

        title_test2("First message")
        title_test2("Second message")

        request = self.factory.get('/title/empty/')
        self.assertEqual(len(MessagesFilter(request).get_queryset()), 0)

    def test_filtering_view_query_m2m_search(self):
        first_tag = [
            "First message", 
            "New",
        ]
        last_tag = [
            "Update",
            "message"
        ]
        four_tag = [
            "Second message",
            "title"
        ]
        six_tag = [
            "Update",
            "title",
            "cats",
            "dogs"
        ]
        first_last_tag = first_tag + last_tag
        four_six_tag = list(set(six_tag + four_tag))
        first_four_last = list(set(first_last_tag + four_tag))

        def test_m2m_tags(link, args_cmp):
            request = self.factory.get(link)
            self.assertQuerysetEqual(
                MessagesFilter(request).get_queryset(), 
                args_cmp, 
                attrgetter("title"),
                ordered = False
            )

        test_m2m_tags('/tags/one/', first_tag)
        test_m2m_tags('/?tags=one', first_tag)

        test_m2m_tags('/tags/one,seven/', first_last_tag)
        test_m2m_tags('/?tags=one,seven', first_last_tag)

        test_m2m_tags('/tags/four,six/', four_six_tag)
        test_m2m_tags('/?tags=four,six', four_six_tag)

        test_m2m_tags('/tags/one,four,seven/', first_four_last)
        test_m2m_tags('/?tags=one,four,seven', first_four_last)

        # last tag should be rejected due the limit in allowed_many
        test_m2m_tags('/tags/one,four,seven,six/', first_four_last)
        test_m2m_tags('/?tags=one,four,seven,six', first_four_last)

    def test_filtering_view_query_complex(self):
        def test_complex(link, args_cmp):
            request = self.factory.get(link)
            self.assertQuerysetEqual(
                MessagesFilter(request).get_queryset(), 
                args_cmp, 
                attrgetter("title"),
                ordered = False
            )

        test_complex('/published/yes/tags/six/', ["cats"])
        test_complex('/?published=yes&tags=six', ["cats"])

        test_complex('/published/yes/tags/seven/title/message/', ["message"])
        test_complex('/?published=yes&tags=seven&title=message', ["message"])
