from django.conf.urls import patterns, include, url
from views import CategoriesListView

urlpatterns = patterns('',
    url(r'categories', CategoriesListView.as_view()),
)
