from django.urls  import path
from .views import *

urlpatterns = [
    path('user', GetUsers.as_view()),
    path('user/new', CreateUser.as_view()),
    path('user/authorization', AuthorizationUser.as_view()),
    path('user/profile/id=<int:user_id>', GetProfile.as_view()),
    path('user/profile', ActivateRefCode.as_view()),
]