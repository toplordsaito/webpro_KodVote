from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my/', views.user_poll, name='poll_user'),
    path('delete/<int:poll_id>', views.deletePoll, name="poll_delete"),
    path('create/', views.createPoll, name='poll_create'),
]
