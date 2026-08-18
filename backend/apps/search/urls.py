from django.urls import path

from .views import global_search

urlpatterns = [
    path("search/", global_search, name="global-search"),
]
