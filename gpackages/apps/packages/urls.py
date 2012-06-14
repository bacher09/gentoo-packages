from django.conf.urls import patterns, include, url
from views import CategoriesListView, HerdsListView

urlpatterns = patterns('',
    url(r'categories/$', CategoriesListView.as_view()),
    url(r'herds/$', HerdsListView.as_view()),
)
