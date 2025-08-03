import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
import json


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
        """Count total votes in this election"""
        return Vote.objects.filter(election_id=self.id).count()

    @property
    def total_voters(self):
        """Count unique voters in this election using anonymous tokens"""
        return (
            Vote.objects.filter(election_id=self.id)
            .values("anonymous_voter_token")
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
        """Count total votes for this position"""
        return Vote.objects.filter(position_id=self.id).count()


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
        """Count votes for this candidate by decrypting vote data"""
        from .crypto import VotingCrypto

        crypto = VotingCrypto()

        count = 0
        votes_for_position = Vote.objects.filter(position_id=self.position.id)

        for vote in votes_for_position:
            try:
                vote_data = crypto.decrypt_vote_data(vote.encrypted_vote_data)
                if vote_data.get("candidate_id") == str(self.id):
                    count += 1
            except Exception:
                # Skip corrupted votes
                continue

        return count

    @property
    def vote_percentage(self):
        total_votes = self.position.total_votes
        if total_votes == 0:
            return 0
        return (self.vote_count / total_votes) * 100


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Remove direct references for anonymity - these are now encrypted
    # voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes")

    # Metadata (only what's absolutely necessary for operations)
    election_id = models.UUIDField()  # Reference to election (needed for queries)
    position_id = models.IntegerField()  # Reference to position (needed for validation)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # All sensitive data is now encrypted
    encrypted_vote_data = (
        models.TextField()
    )  # Contains voter_id, candidate_id, and other details
    vote_hash = models.CharField(max_length=64)  # Cryptographic hash for integrity
    digital_signature = models.TextField()  # Digital signature
    anonymous_voter_token = models.CharField(
        max_length=32, unique=True
    )  # Anonymized voter ID

    # Verification status
    signature_verified = models.BooleanField(default=False)
    integrity_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["election_id", "timestamp"]),
            models.Index(fields=["position_id", "timestamp"]),
            models.Index(fields=["anonymous_voter_token"]),
            models.Index(fields=["timestamp"]),
        ]
        constraints = [
            # Ensure one vote per anonymous token per position
            models.UniqueConstraint(
                fields=["anonymous_voter_token", "position_id"],
                name="unique_anonymous_vote_per_position",
            )
        ]

    def __str__(self):
        return f"Anonymous vote {self.id[:8]} in election {self.election_id}"

    @classmethod
    def create_secure_vote(cls, voter, candidate, ip_address=None):
        """
        Create a new secure anonymous vote with encryption and digital signature.
        No direct references to voter or candidate are stored.
        """
        from .crypto import VotingCrypto, DigitalSignature

        crypto = VotingCrypto()
        signature_util = DigitalSignature()

        # Create vote data (this will be encrypted)
        vote_data = {
            "voter_id": str(voter.id),
            "voter_username": voter.username,
            "voter_student_id": getattr(voter, "student_id", ""),
            "candidate_id": str(candidate.id),
            "candidate_name": (
                str(candidate.user.student_id) if candidate.user else "Unknown"
            ),
            "position_id": str(candidate.position.id),
            "position_title": candidate.position.title,
            "election_id": str(candidate.position.election.id),
            "election_title": candidate.position.election.title,
            "timestamp": timezone.now().isoformat(),
        }

        # Encrypt vote data (contains all sensitive information)
        encrypted_data = crypto.encrypt_vote_data(vote_data)

        # Generate cryptographic hash for integrity
        vote_hash = crypto.generate_vote_hash(
            vote_data["voter_id"],
            vote_data["candidate_id"],
            vote_data["position_id"],
            vote_data["election_id"],
            vote_data["timestamp"],
        )

        # Create digital signature
        vote_bytes = json.dumps(vote_data, sort_keys=True).encode()
        signature = signature_util.sign_vote(vote_bytes)

        # Create anonymous voter token (allows checking for duplicate votes without revealing identity)
        anonymous_token = crypto.anonymize_voter_data(
            str(voter.id), str(candidate.position.election.id)
        )

        # Check if this voter has already voted for this position
        existing_vote = cls.objects.filter(
            anonymous_voter_token=anonymous_token, position_id=candidate.position.id
        ).first()

        if existing_vote:
            raise ValueError("This voter has already voted for this position")

        # Create the anonymous secure vote
        secure_vote = cls.objects.create(
            election_id=candidate.position.election.id,
            position_id=candidate.position.id,
            ip_address=ip_address,
            encrypted_vote_data=encrypted_data,
            vote_hash=vote_hash,
            digital_signature=signature.hex(),
            anonymous_voter_token=anonymous_token,
            signature_verified=True,
            integrity_verified=True,
        )

        return secure_vote

    @classmethod
    def has_voter_voted_for_position(cls, voter, position):
        """
        Check if a voter has already voted for a specific position
        using anonymous token (preserves anonymity)
        """
        from .crypto import VotingCrypto

        crypto = VotingCrypto()

        anonymous_token = crypto.anonymize_voter_data(
            str(voter.id), str(position.election.id)
        )

        return cls.objects.filter(
            anonymous_voter_token=anonymous_token, position_id=position.id
        ).exists()

    @classmethod
    def get_election_results(cls, election):
        """
        Get election results by decrypting votes (admin only)
        Returns a dictionary with candidate vote counts
        """
        from .crypto import VotingCrypto

        crypto = VotingCrypto()

        results = {}
        votes = cls.objects.filter(election_id=election.id)

        for vote in votes:
            try:
                vote_data = crypto.decrypt_vote_data(vote.encrypted_vote_data)
                candidate_id = vote_data.get("candidate_id")
                position_id = vote_data.get("position_id")

                if position_id not in results:
                    results[position_id] = {}

                if candidate_id not in results[position_id]:
                    results[position_id][candidate_id] = 0

                results[position_id][candidate_id] += 1

            except Exception:
                # Skip corrupted votes
                continue

        return results

    def decrypt_vote_data(self):
        """
        Decrypt and return vote data (admin only)
        """
        if not self.encrypted_vote_data:
            return None

        from .crypto import VotingCrypto

        crypto = VotingCrypto()
        return crypto.decrypt_vote_data(self.encrypted_vote_data)

    def verify_integrity(self):
        """
        Verify vote integrity using cryptographic hash and digital signature
        """
        if not self.encrypted_vote_data:
            return False

        try:
            from .crypto import VotingCrypto, DigitalSignature

            crypto = VotingCrypto()
            signature_util = DigitalSignature()

            # Decrypt vote data
            vote_data = self.decrypt_vote_data()

            # Verify hash
            hash_valid = crypto.verify_vote_integrity(
                self.vote_hash,
                vote_data["voter_id"],
                vote_data["candidate_id"],
                vote_data["position_id"],
                vote_data["election_id"],
                vote_data["timestamp"],
            )

            # Verify digital signature
            vote_bytes = json.dumps(vote_data, sort_keys=True).encode()
            signature_bytes = bytes.fromhex(self.digital_signature)
            signature_valid = signature_util.verify_vote_signature(
                vote_bytes, signature_bytes
            )

            # Update verification status
            self.integrity_verified = hash_valid
            self.signature_verified = signature_valid
            self.save(update_fields=["integrity_verified", "signature_verified"])

            return hash_valid and signature_valid

        except Exception:
            return False

    def get_candidate_info(self):
        """
        Get candidate information from encrypted vote data (admin only)
        Returns candidate object if found, None otherwise
        """
        try:
            vote_data = self.decrypt_vote_data()
            if vote_data:
                candidate_id = vote_data.get("candidate_id")
                return Candidate.objects.get(id=candidate_id)
        except Exception:
            pass
        return None

    def get_voter_info(self):
        """
        Get voter information from encrypted vote data (admin only)
        Returns basic voter info without revealing identity in logs
        """
        try:
            vote_data = self.decrypt_vote_data()
            if vote_data:
                return {
                    "voter_id": vote_data.get("voter_id"),
                    "voter_username": vote_data.get("voter_username"),
                    "voter_student_id": vote_data.get("voter_student_id"),
                }
        except Exception:
            pass
        return None


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


class AuditLog(models.Model):
    """Comprehensive audit logging for all system actions"""

    ACTION_CHOICES = [
        ("vote_cast", "Vote Cast"),
        ("vote_viewed", "Vote Viewed"),
        ("election_created", "Election Created"),
        ("election_updated", "Election Updated"),
        ("election_deleted", "Election Deleted"),
        ("candidate_added", "Candidate Added"),
        ("candidate_removed", "Candidate Removed"),
        ("results_generated", "Results Generated"),
        ("user_login", "User Login"),
        ("user_logout", "User Logout"),
        ("admin_access", "Admin Access"),
        ("data_export", "Data Export"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    resource_type = models.CharField(
        max_length=50
    )  # 'election', 'vote', 'candidate', etc.
    resource_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)

    # Security fields
    integrity_hash = models.CharField(max_length=64)  # SHA-256 hash for integrity

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Generate integrity hash before saving
        if not self.integrity_hash:
            from .crypto import VotingCrypto

            crypto = VotingCrypto()
            audit_data = {
                "action": self.action,
                "user_id": str(self.user.id) if self.user else "anonymous",
                "resource_type": self.resource_type,
                "resource_id": self.resource_id,
                "timestamp": self.timestamp.isoformat() if self.timestamp else "",
                "details": self.details,
            }
            self.integrity_hash = crypto.generate_election_audit_hash(audit_data)

        super().save(*args, **kwargs)


class ElectionSecurity(models.Model):
    """Security configuration for elections"""

    election = models.OneToOneField(
        Election, on_delete=models.CASCADE, related_name="security"
    )

    # Security settings
    enable_vote_encryption = models.BooleanField(default=True)
    enable_digital_signatures = models.BooleanField(default=True)
    enable_audit_logging = models.BooleanField(default=True)
    enable_ip_verification = models.BooleanField(default=True)

    # Rate limiting
    max_votes_per_minute = models.IntegerField(default=5)
    max_login_attempts = models.IntegerField(default=3)

    # Access controls
    require_two_factor_auth = models.BooleanField(default=False)
    whitelist_ip_addresses = models.JSONField(default=list, blank=True)

    # Audit settings
    log_all_access = models.BooleanField(default=True)
    log_failed_attempts = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Security settings for {self.election.title}"


class VotingSession(models.Model):
    """Track voting sessions for security monitoring"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    # Session metadata
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # Security tracking
    votes_cast = models.IntegerField(default=0)
    is_suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(blank=True)

    # Geolocation (optional)
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "election"]),
            models.Index(fields=["session_start"]),
            models.Index(fields=["is_suspicious"]),
        ]

    def __str__(self):
        return f"Voting session {self.id[:8]} for {self.user} in {self.election.title}"

    def mark_suspicious(self, reason):
        """Mark session as suspicious with reason"""
        self.is_suspicious = True
        self.suspicious_reason = reason
        self.save(update_fields=["is_suspicious", "suspicious_reason"])

    def end_session(self):
        """End the voting session"""
        self.session_end = timezone.now()
        self.save(update_fields=["session_end"])
