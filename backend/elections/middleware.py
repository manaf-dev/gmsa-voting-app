"""
Security middleware for voting system
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.core.cache import cache, caches
from django.conf import settings
from .models import AuditLog, VotingSession
from .crypto import create_audit_entry


User = get_user_model()


class SecurityMiddleware(MiddlewareMixin):
    """Enhanced security middleware for voting system"""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """Process incoming requests for security checks"""

        # Rate limiting check
        if self._is_rate_limited(request):
            return JsonResponse(
                {"error": "Rate limit exceeded. Please try again later."}, status=429
            )

        # IP whitelist check (for sensitive operations)
        if self._requires_ip_whitelist(request) and not self._is_ip_whitelisted(
            request
        ):
            return JsonResponse(
                {"error": "Access denied from this IP address."}, status=403
            )

        return None

    def process_response(self, request, response):
        """Process responses for audit logging"""

        # Log security-relevant actions
        if hasattr(request, "user") and request.user.is_authenticated:
            self._log_user_action(request, response)

        return response

    def _is_rate_limited(self, request):
        """Check if request should be rate limited"""

        # Get client IP
        ip = self._get_client_ip(request)

        # Different limits for different endpoints
        limits = {
            "/api/elections/vote/": (10, 60),  # 10 votes per minute
            "/api/auth/login/": (5, 300),  # 5 login attempts per 5 minutes
            "/api/auth/register/": (3, 3600),  # 3 registrations per hour
        }

        for endpoint, (max_requests, window) in limits.items():
            if request.path.startswith(endpoint):
                return self._check_rate_limit(ip, endpoint, max_requests, window)

        # Default rate limit
        return self._check_rate_limit(ip, "default", 60, 60)  # 60 requests per minute

    def _check_rate_limit(self, key, endpoint, max_requests, window):
        """Check rate limit for specific key and endpoint"""

        cache_key = f"rate_limit:{endpoint}:{key}"
        try:
            current_requests = cache.get(cache_key, 0)
        except Exception:
            # Fallback to local memory cache if default cache (Redis) is unavailable
            try:
                local_cache = caches["local"]
            except Exception:
                local_cache = cache
            current_requests = local_cache.get(cache_key, 0)

        if current_requests >= max_requests:
            return True

        # Increment counter
        try:
            cache.set(cache_key, current_requests + 1, window)
        except Exception:
            try:
                local_cache = caches["local"]
            except Exception:
                local_cache = cache
            local_cache.set(cache_key, current_requests + 1, window)
        return False

    def _requires_ip_whitelist(self, request):
        """Check if request requires IP whitelisting"""

        sensitive_endpoints = [
            "/api/admin/",
            "/api/elections/results/generate/",
            "/api/elections/export/",
        ]

        return any(
            request.path.startswith(endpoint) for endpoint in sensitive_endpoints
        )

    def _is_ip_whitelisted(self, request):
        """Check if IP is whitelisted for sensitive operations"""

        # In production, this would check against database/config
        whitelisted_ips = getattr(settings, "WHITELISTED_IPS", [])
        client_ip = self._get_client_ip(request)

        return client_ip in whitelisted_ips or not whitelisted_ips

    def _get_client_ip(self, request):
        """Get real client IP address"""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip

    def _log_user_action(self, request, response):
        """Log user actions for audit trail"""

        # Only log certain actions
        loggable_actions = {
            "POST": ["vote", "login", "register", "create", "delete"],
            "PUT": ["update", "edit"],
            "DELETE": ["delete", "remove"],
            "GET": ["results", "export", "admin"],
        }

        method = request.method
        path = request.path.lower()

        # Check if action should be logged
        if method in loggable_actions:
            for action in loggable_actions[method]:
                if action in path:
                    self._create_audit_log(request, response, action)
                    break

    def _create_audit_log(self, request, response, action):
        """Create audit log entry"""

        try:
            # Determine resource type and ID from path
            resource_type, resource_id = self._parse_resource_from_path(request.path)

            # Create audit entry
            audit_data = create_audit_entry(
                action=action,
                user_id=str(request.user.id),
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "content_length": (
                        len(response.content) if hasattr(response, "content") else 0
                    ),
                },
            )

            # Save to database
            AuditLog.objects.create(
                action=action,
                user=request.user,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                details=audit_data["details"],
            )

        except Exception as e:
            # Log error but don't break the request
            print(f"Audit logging error: {e}")

    def _parse_resource_from_path(self, path):
        """Parse resource type and ID from request path"""

        parts = path.strip("/").split("/")

        if "elections" in parts:
            idx = parts.index("elections")
            if len(parts) > idx + 1:
                return "election", parts[idx + 1]
            return "election", "unknown"

        if "candidates" in parts:
            idx = parts.index("candidates")
            if len(parts) > idx + 1:
                return "candidate", parts[idx + 1]
            return "candidate", "unknown"

        if "positions" in parts:
            idx = parts.index("positions")
            if len(parts) > idx + 1:
                return "position", parts[idx + 1]
            return "position", "unknown"

        return "unknown", "unknown"


class VotingSessionMiddleware(MiddlewareMixin):
    """Track voting sessions for security monitoring"""

    def process_request(self, request):
        """Track voting session start"""

        if (
            hasattr(request, "user")
            and request.user.is_authenticated
            and "elections" in request.path
            and "vote" in request.path
        ):

            self._start_or_update_session(request)

        return None

    def _start_or_update_session(self, request):
        """Start new voting session or update existing one"""

        try:
            # Extract election ID from path
            election_id = self._extract_election_id(request.path)
            if not election_id:
                return

            from elections.models import Election

            election = Election.objects.get(id=election_id)

            # Get or create voting session
            session, created = VotingSession.objects.get_or_create(
                user=request.user,
                election=election,
                session_end__isnull=True,  # Active session
                defaults={
                    "ip_address": self._get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                },
            )

            # Check for suspicious activity
            self._check_suspicious_activity(session, request)

        except Exception as e:
            print(f"Session tracking error: {e}")

    def _extract_election_id(self, path):
        """Extract election ID from request path"""

        parts = path.strip("/").split("/")
        if "elections" in parts:
            idx = parts.index("elections")
            if len(parts) > idx + 1:
                return parts[idx + 1]

        return None

    def _check_suspicious_activity(self, session, request):
        """Check for suspicious voting activity"""

        current_ip = self._get_client_ip(request)

        # Check for IP address changes
        if session.ip_address != current_ip:
            session.mark_suspicious("IP address changed during session")

        # Check for rapid voting
        recent_votes = session.votes_cast
        if recent_votes > 10:  # More than 10 votes in session
            session.mark_suspicious("Unusually high number of votes")

        # Check for user agent changes
        current_ua = request.META.get("HTTP_USER_AGENT", "")
        if session.user_agent != current_ua:
            session.mark_suspicious("User agent changed during session")

    def _get_client_ip(self, request):
        """Get real client IP address"""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip


class SecureHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""

    def process_response(self, request, response):
        """Add security headers"""

        # Content Security Policy
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Security headers
        response["X-Frame-Options"] = "DENY"
        response["X-Content-Type-Options"] = "nosniff"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # HSTS (if HTTPS)
        if request.is_secure():
            response["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
