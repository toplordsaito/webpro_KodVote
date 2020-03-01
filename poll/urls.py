from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my/', views.user_poll, name='poll_user'),
    path('view/<int:poll_id>/', views.viewPoll, name="poll_view"),
    path('delete/<int:poll_id>/', views.deletePoll, name="poll_delete"),
    path('update/<int:poll_id>/', views.updatePoll, name='poll_update'),
    path('vote/<int:poll_id>/', views.votePoll, name='poll_vote'),
    path('addChoice/<int:poll_id>/', views.createChoice, name='choice_create'),
    path('deleteChoice/<int:choice_id>/',
         views.deleteChoice, name='choice_delete'),
    path('create/', views.createPoll, name='poll_create'),
]
