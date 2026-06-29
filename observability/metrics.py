from prometheus_client import Counter, Gauge, Histogram

# General Request Metrics
GATEWAY_REQUESTS_TOTAL = Counter(
    "gateway_requests_total",
    "Total number of requests handled by the gateway",
    ["method", "service", "status"]
)

GATEWAY_REQUEST_DURATION = Histogram(
    "gateway_request_duration_seconds",
    "Request duration in seconds",
    ["method", "service"]
)

GATEWAY_ACTIVE_REQUESTS = Gauge(
    "gateway_active_requests",
    "Number of requests currently being processed"
)

# Error Metrics
GATEWAY_4XX_TOTAL = Counter(
    "gateway_4xx_total",
    "Total number of 4xx responses",
    ["service"]
)

GATEWAY_5XX_TOTAL = Counter(
    "gateway_5xx_total",
    "Total number of 5xx responses",
    ["service"]
)

# Request / Response Size
GATEWAY_REQUEST_SIZE = Histogram(
    "gateway_request_size_bytes",
    "Request size in bytes",
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000, float("inf"))
)

GATEWAY_RESPONSE_SIZE = Histogram(
    "gateway_response_size_bytes",
    "Response size in bytes",
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000, float("inf"))
)

# Cache Metrics
GATEWAY_CACHE_HITS = Counter(
    "gateway_cache_hits_total",
    "Total number of cache hits"
)

GATEWAY_CACHE_MISSES = Counter(
    "gateway_cache_misses_total",
    "Total number of cache misses"
)

# Rate Limiter Metrics
GATEWAY_RATE_LIMIT_HITS = Counter(
    "gateway_rate_limit_hits_total",
    "Total number of rate limited requests"
)

# Resilience Metrics
GATEWAY_RETRY_TOTAL = Counter(
    "gateway_retry_total",
    "Total number of retries executed",
    ["service"]
)

GATEWAY_TIMEOUT_TOTAL = Counter(
    "gateway_timeout_total",
    "Total number of upstream timeouts",
    ["service"]
)

GATEWAY_CIRCUIT_OPEN_TOTAL = Counter(
    "gateway_circuit_open_total",
    "Total number of times a circuit breaker opened",
    ["service"]
)
