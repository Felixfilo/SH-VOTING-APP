from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('vote/<int:candidate_id>/confirm/', views.vote_confirm, name='vote_confirm'),
    path('vote/success/', views.vote_success, name='vote_success'),
    path('already-voted/', views.already_voted_view, name='already_voted'),
    path('not-eligible/', views.not_eligible_view, name='not_eligible'),
    path('no-election/', views.no_election_view, name='no_election'),
    path('voting-not-started/', views.voting_not_started_view, name='voting_not_started'),
    path('voting-ended/', views.voting_ended_view, name='voting_ended'),
]
