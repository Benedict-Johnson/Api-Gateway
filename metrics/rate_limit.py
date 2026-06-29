from prometheus_client import Counter

allowed_requests = Counter(
    "gateway_rate_limit_allowed",
    "Allowed Requests"
)

blocked_requests = Counter(
    "gateway_rate_limit_blocked",
    "Blocked Requests"
)