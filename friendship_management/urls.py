from django.urls import path
from friendship_management.views import (
    FriendRequestView,
    FriendListView
)
urlpatterns = [
    path('request/', FriendRequestView.as_view()),
    path('list/', FriendListView.as_view()),
]