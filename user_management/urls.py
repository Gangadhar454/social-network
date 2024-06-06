from django.urls import path
from user_management.views import (
    UserSignupView,
    UserSignInView
)
urlpatterns = [
    path('signup/', UserSignupView.as_view()),
    path('login/', UserSignInView.as_view()),
]