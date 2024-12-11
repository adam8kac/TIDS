# myapp/urls.py
from django.urls import path
from myapp.views.user_view import UserListCreate, UserDetail

urlpatterns = [
    path('', UserListCreate.as_view(), name="user-list-create"),
    path('<int:pk>/', UserDetail.as_view(), name="user-detail"), 
]
