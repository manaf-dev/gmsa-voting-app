from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet
import secrets
import json


class Command(BaseCommand):
    help = (
        "Generate secrets for voting security: VOTING_ENCRYPTION_KEY, "
        "VOTE_HASH_SECRET, and VOTER_ANONYMIZATION_SALT"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            choices=["env", "json"],
            default="env",
            help="Output format (default: env)",
        )

    def handle(self, *args, **options):
        # Generate a valid Fernet key (base64 urlsafe, 32-byte decoded)
        voting_encryption_key = Fernet.generate_key().decode()
        # Strong, urlsafe secrets for hashing and anonymization salt
        vote_hash_secret = secrets.token_urlsafe(64)
        voter_anonymization_salt = secrets.token_urlsafe(32)

        if options.get("format") == "json":
            payload = {
                "VOTING_ENCRYPTION_KEY": voting_encryption_key,
                "VOTE_HASH_SECRET": vote_hash_secret,
                "VOTER_ANONYMIZATION_SALT": voter_anonymization_salt,
            }
            self.stdout.write(json.dumps(payload, indent=2))
            return

        # Default .env style output
        self.stdout.write(self.style.SUCCESS("# Add these to your backend .env file"))
        self.stdout.write(f"VOTING_ENCRYPTION_KEY={voting_encryption_key}")
        self.stdout.write(f"VOTE_HASH_SECRET={vote_hash_secret}")
        self.stdout.write(f"VOTER_ANONYMIZATION_SALT={voter_anonymization_salt}")
        self.stdout.write("")
        self.stdout.write(
            "Note: Restart your server after updating the .env so settings reload."
        )
