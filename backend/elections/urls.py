from django.urls import path
from . import views

urlpatterns = [
    path("", views.ElectionListCreateView.as_view(), name="election-list-create"),
    path("<uuid:pk>/", views.ElectionDetailView.as_view(), name="election-detail"),
    path("<uuid:election_id>/vote/", views.cast_vote, name="cast-vote"),
    path("<uuid:election_id>/my-votes/", views.user_votes, name="user-votes"),
    path(
        "<uuid:election_id>/results/", views.election_results, name="election-results"
    ),
    path(
        "<uuid:election_id>/generate-results/",
        views.generate_election_results,
        name="generate-results",
    ),
]
