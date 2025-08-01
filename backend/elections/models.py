import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Election(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_elections",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Election settings
    allow_multiple_votes_per_position = models.BooleanField(default=False)
    require_dues_payment = models.BooleanField(default=False)
    show_results_after_voting = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.status == "active" and self.start_date <= now <= self.end_date

    @property
    def can_vote(self):
        return self.is_active

    @property
    def total_votes(self):
        return Vote.objects.filter(candidate__position__election=self).count()

    @property
    def total_voters(self):
        return (
            Vote.objects.filter(candidate__position__election=self)
            .values("voter")
            .distinct()
            .count()
        )


class Position(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name="positions"
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_candidates = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]
        unique_together = ["election", "title"]

    def __str__(self):
        return f"{self.election.title} - {self.title}"

    @property
    def total_votes(self):
        return Vote.objects.filter(candidate__position=self).count()


class Candidate(models.Model):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="candidates"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidates",
        null=True,
        blank=True,
    )
    manifesto = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["position", "user"],
                name="unique_candidate_per_position_per_user",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.student_id if self.user else 'User'} - {self.position.title}"
        )

    @property
    def vote_count(self):
        return self.votes.count()

    @property
    def vote_percentage(self):
        total_votes = self.position.total_votes
        if total_votes == 0:
            return 0
        return (self.vote_count / total_votes) * 100


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="votes"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["voter", "candidate"],
                name="unique_vote_per_candidate_per_voter",
            ),
        ]
        indexes = [
            models.Index(fields=["voter", "timestamp"]),
            models.Index(fields=["candidate", "timestamp"]),
        ]

    def __str__(self):
        return f"Vote by {self.voter.username} for {self.candidate.name}"


class ElectionResult(models.Model):
    election = models.OneToOneField(
        Election, on_delete=models.CASCADE, related_name="result"
    )
    total_eligible_voters = models.PositiveIntegerField()
    total_votes_cast = models.PositiveIntegerField()
    voter_turnout_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Results for {self.election.title}"
