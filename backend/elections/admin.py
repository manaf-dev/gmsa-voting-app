from django.contrib import admin
from .models import Election, Position, Candidate, Vote, ElectionResult, VotingSession, AuditLog, ElectionSecurity


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "start_date",
        "end_date",
        "total_votes",
        "total_voters",
    )
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("title", "description")
    inlines = [PositionInline]
    readonly_fields = ("total_votes", "total_voters")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "election", "total_votes")
    list_filter = ("election",)
    search_fields = ("title", "election__title")
    inlines = [CandidateInline]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("position", "vote_count")
    list_filter = ("position__election", "position")
    search_fields = ("user__student_id", "position__title")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "election_id",
        "position_id",
        "anonymous_voter_token",
        "timestamp",
        "integrity_verified",
        "signature_verified",
    )
    list_filter = ("timestamp", "integrity_verified", "signature_verified")
    search_fields = ("anonymous_voter_token", "election_id")
    readonly_fields = (
        "id",
        "election_id",
        "position_id",
        "timestamp",
        "ip_address",
        "encrypted_vote_data",
        "vote_hash",
        "digital_signature",
        "anonymous_voter_token",
        "integrity_verified",
        "signature_verified",
    )


@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = (
        "election",
        "total_eligible_voters",
        "total_votes_cast",
        "voter_turnout_percentage",
        "generated_at",
    )
    readonly_fields = ("generated_at",)


@admin.register(VotingSession)
class VotingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_start",
        "session_end",
    )
    readonly_fields = ("session_start", "session_end")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "timestamp",
    )
    readonly_fields = ("timestamp",)

@admin.register(ElectionSecurity)
class ElectionSecurityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "election",
    )
