from rest_framework.throttling import UserRateThrottle
from django.conf import settings

class MemberRateThrottle(UserRateThrottle):
    # Define a custom scope name to be referenced by DRF in settings.py
    scope = "member"

    def __init__(self):
        super().__init__()

    def allow_request(self, request, view):
        """
        Override rest_framework.throttling.SimpleRateThrottle.allow_request

        Check to see if the request should be throttled.

        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if request.user.is_staff:
            # No throttling
            return True

        if request.user.is_authenticated:
            self.key, self.num_requests = get_user_throttle_data(request.user)
        else:
            # Unauthenticated user will be blocked by authentication guard
            # Returning False will give the user a throttle error instead of an authentication error
            return True

        # Original logic from the parent method (besides cache key determination)

        if self.rate is None or self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

# Returns the cache key associated with the incoming request and the applicable rate limit
def get_user_throttle_data(user):
    # If user works for SunSpec Alliance member, return MemberID cache key and standard member limit 
    if user.MemberID:
        return f'Member{user.MemberID.MemberID}', settings.SUNSPEC_MEMBER_API_THROTTLE_RATE
    # Else user is regular, returns user pk cache key and standard user rate
    else:
        return user.pk, settings.DEFAULT_API_THROTTLE_RATE