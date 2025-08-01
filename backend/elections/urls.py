from django.urls import path
from . import views

urlpatterns = [
    # Election URLs
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
    # Position URLs
    path(
        "<uuid:election_id>/positions/",
        views.PositionListCreateView.as_view(),
        name="position-list-create",
    ),
    path(
        "positions/<uuid:pk>/",
        views.PositionDetailView.as_view(),
        name="position-detail",
    ),
    # Candidate URLs
    path(
        "positions/<uuid:position_id>/candidates/",
        views.CandidateListCreateView.as_view(),
        name="candidate-list-create",
    ),
    path(
        "candidates/<uuid:pk>/",
        views.CandidateDetailView.as_view(),
        name="candidate-detail",
    ),
    # Admin URLs
    path("admin/stats/", views.admin_stats, name="admin-stats"),
    path("admin/members/", views.admin_members, name="admin-members"),
    path("admin/members/export/", views.export_members, name="export-members"),
    path(
        "admin/members/<int:member_id>/reminder/",
        views.send_reminder,
        name="send-reminder",
    ),
]
