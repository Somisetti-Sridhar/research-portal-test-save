from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('advanced/', views.AdvancedSearchView.as_view(), name='advanced'),
    path('suggestions/', views.search_suggestions, name='suggestions'),
    path('history/', views.SearchHistoryView.as_view(), name='history'),
]
