# myapp/urls.py
from django.urls import path
from myapp.views.user_view import UserListCreate, UserDetail
from myapp.views.scraper_view import scrape_data_view

urlpatterns = [
    path('', UserListCreate.as_view(), name="user-list-create"),
    path('<int:pk>/', UserDetail.as_view(), name="user-detail"),
    path('api/scrape-data/', scrape_data_view, name='scrape_data'),
]
