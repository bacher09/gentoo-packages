"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import models 
from . import models as stats
from datetime import date

class Tag(stats.StatsModel):
    stats_params = (
        ('books_count', 'book'),
        ('authors_count', 'book__authors'),
        ('publishers_count', 'book__publishers'),
    )
    name = models.CharField(unique = True, max_length = 40)

    def __unicode__(self):
        return self.name

class Author(stats.StatsModel):
    stats_params = (
        ('books_count', 'book'),
        ('publishers_count', 'book__publishers'),
        ('tags_count', 'book__tags'),
    )

    name = models.CharField(max_length = 60)
    birth_day = models.DateField(blank = True, null = True)
    
    def __unicode__(self):
        return self.name

class Publisher(stats.StatsModel):
    stats_params = (
        ('books_count', 'book'),
        ('tags_count', 'book__tags'),
        ('authors_count', 'book__authors'),
    )
    name = models.CharField(unique = True, max_length = 60)
    
    def __unicode__(self):
        return self.name

class Book(stats.StatsModel):
    stats_params = (
        ('authors_count', 'authors'),
        ('tags_count', 'tags'),
        ('publishers_count', 'publishers'),
        ('review_count', 'review'),
    )
    title = models.CharField(max_length = 60)
    description = models.TextField(blank = True)
    authors = models.ManyToManyField(Author)
    tags = models.ManyToManyField(Tag)
    publishers = models.ManyToManyField(Publisher)
    price = models.DecimalField(blank = True, null = True,
                                max_digits=5, decimal_places=2)
    
    def __unicode__(self):
        return self.name

class Review(models.Model):
    text = models.TextField()
    book = models.ForeignKey(Book)

    def __unicode__(self):
        return self.text

def get_objects_by_id(obj_list, ids_list):
    return [obj_list[i] for i in ids_list]

class SimpleTest(TestCase):
    models_list = [Tag, Publisher, Review, Book]
    tags_list = ["one", "two", "three", "four", "five", "six", "seven"]
    tags_stats = [
        {'books_count' : 1, 'authors_count' : 1, 'publishers_count' : 2},
        {'books_count' : 3, 'authors_count' : 3, 'publishers_count' : 3},
        {'books_count' : 4, 'authors_count' : 3, 'publishers_count' : 3},
        {'books_count' : 9, 'authors_count' : 4, 'publishers_count' : 2},
        {'books_count' : 7, 'authors_count' : 3, 'publishers_count' : 3},
        {'books_count' : 2, 'authors_count' : 2, 'publishers_count' : 2},
        {'books_count' : 3, 'authors_count' : 3, 'publishers_count' : 3}
    ]
    authors_list = [
        {'name' : 'John Doe', 'birth_day' : date(1976, 3, 2)},
        {'name' : 'Donald Knuth', 'birth_day' : date(1938, 1, 10)},
        {'name' : 'Richard Stevens', 'birth_day' : date(1951, 2, 5)},
        {'name' : 'Niklaus Wirth', 'birth_day' : date(1934, 2, 15)},
        {'name' : 'Larry Wall', 'birth_day' : date(1954, 9, 27)},
    ]
    authors_stats = [
        {'books_count' : 2, 'tags_count' : 4, 'publishers_count' : 2},
        {'books_count' : 5, 'tags_count' : 5, 'publishers_count' : 2},
        {'books_count' : 3, 'tags_count' : 4, 'publishers_count' : 3},
        {'books_count' : 1, 'tags_count' : 3, 'publishers_count' : 2},
        {'books_count' : 1, 'tags_count' : 3, 'publishers_count' : 1},
    ]

    publishers_list = ["O'Reilly", "Addison-Wesley", "Apress"]
    publishers_stats = [
        {'books_count' : 5, 'tags_count' : 6, 'authors_count' : 5},
        {'books_count' : 9, 'tags_count' : 7, 'authors_count' : 3},
        {'books_count' : 2, 'tags_count' : 5, 'authors_count' : 2}
    ]

    books_list = [
        ({'title' : 'Test', 'price' : 10}, [0], [0,1,2,3], [0,1]),
        (
         {'title' : 'The Art of Computer Programming vol 1', 'price' : 40.01},
         [1], [3, 4], [1]
        ),
        (
         {'title' : 'The Art of Computer Programming vol 2', 'price' : 30.11},
         [1], [1, 3, 4], [1, 0]
        ),
        (
         {'title' : 'The Art of Computer Programming vol 3', 'price' : 42.99},
         [1], [3, 4, 5], [1]
        ),
        (
         {'title' : 'The Art of Computer Programming vol 4', 'price' : 41.80},
         [1], [3, 4], [1]
        ),
        (
         {'title' : 'The Art of Computer Programming vol 5', 'price' : 40.91},
         [1], [3, 4, 6], [1]
        ),
        (
         {'title' : 'TCP/IP Illustrated vol 1', 'price' : 30.03},
         [2], [5, 6], [1, 2]
        ),
        (
         {'title' : 'TCP/IP Illustrated vol 2', 'price' : 33.13},
         [2], [2, 3], [1]
        ),
        (
         {'title' : 'TCP/IP Illustrated vol 3', 'price' : 37.12},
         [2, 0], [2, 3], [1, 0]
        ),
        (
         {'title' : 'Algorithms + Data Structures ', 'price' : 39.19},
         [3], [4, 1, 2], [0, 2]
        ),
        (
         {'title' : 'Programming Perl', 'price' : 36.12},
         [4], [3, 6, 4], [0]
        ),
    ]

    books_stats = [
        { 'authors_count' : 1, 'tags_count' : 4,
          'publishers_count' : 2, 'review_count': 1
        },
        { 'authors_count' : 1, 'tags_count' : 2,
          'publishers_count' : 1, 'review_count': 2
        },
        { 'authors_count' : 1, 'tags_count' : 3,
          'publishers_count' : 2, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 3,
          'publishers_count' : 1, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 2,
          'publishers_count' : 1, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 3,
          'publishers_count' : 1, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 2,
          'publishers_count' : 2, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 2,
          'publishers_count' : 1, 'review_count': 0
        },
        { 'authors_count' : 2, 'tags_count' : 2,
          'publishers_count' : 2, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 3,
          'publishers_count' : 2, 'review_count': 0
        },
        { 'authors_count' : 1, 'tags_count' : 3,
          'publishers_count' : 1, 'review_count': 2
        },
    ]

    reviews_list = [(0, 'Bad'),
                    (1, 'Good'),
                    (1, "Very good"),
                    (10, "Good"),
                    (10, "Cool")
    ]

    def setUp(self):
        tags_obj = []
        for tag in self.tags_list:
            tags_obj.append(Tag.objects.create(name = tag))

        authors_obj = []
        for author in self.authors_list:
            authors_obj.append(Author.objects.create(**author))

        publishers_obj = []
        for publisher in self.publishers_list:
            publishers_obj.append(Publisher.objects.create(name = publisher))

        books_obj = []
        for book, author_id, tags_id, publishers_id in self.books_list:
            b = Book.objects.create(**book)
            b.authors.add(*get_objects_by_id(authors_obj, author_id))
            b.tags.add(*get_objects_by_id(tags_obj, tags_id))
            b.publishers.add(*get_objects_by_id(publishers_obj, publishers_id))
            books_obj.append(b)

        for book_id, review in self.reviews_list:
            Review.objects.create(book = books_obj[book_id], text = review)

    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)

    def test_models_search(self):
        models_set = set()
        for model in stats.filter_models(self.models_list):
            models_set.add(model)

        self.assertEqual(models_set, set([Tag, Publisher, Book]))

    def test_models_auto_fields(self):
        one = Tag.objects.get(name = "one")
        one.books_count = 10
        one.save()
        one = Tag.objects.get(name = "one")
        self.assertEqual(one.books_count, 10)

    def test_stats_calc(self):
        stats.update_stats_for_models([Tag, Author, Publisher, Book])
        pubs = Publisher.objects.all(). \
            values('books_count', 'authors_count', 'tags_count')
        for num, pub in enumerate(pubs):
            self.assertEqual(pub, self.publishers_stats[num])

        tags = Tag.objects.all(). \
            values('books_count', 'authors_count', 'publishers_count')
        for num, tag in enumerate(tags):
            self.assertEqual(tag, self.tags_stats[num])

        authors = Author.objects.all(). \
            values('books_count', 'tags_count', 'publishers_count')
        for num, author in enumerate(authors):
            self.assertEqual(author, self.authors_stats[num])

        books = Book.objects.all(). \
            values('authors_count', 'tags_count', 
                   'publishers_count', 'review_count')
        for num, book in enumerate(books):
            self.assertEqual(book, self.books_stats[num])

