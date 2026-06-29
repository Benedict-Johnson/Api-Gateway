import sys

from routing.registry import RouteRegistry
from load_balancer.registry import ServiceRegistry
from config.retry import RetryLoader
from config.timeout import TimeoutLoader
from config.circuit_breaker import CircuitBreakerLoader
from cache.config import CacheConfigLoader
from rate_limiter.config import RateLimitLoader

def fail(file: str, field: str, reason: str):
    print("\n" + "="*40, flush=True)
    print("CONFIG VALIDATION FAILED", flush=True)
    print("="*40, flush=True)
    print(f"\nFile:\n{file}\n", flush=True)
    print(f"Field:\n{field}\n", flush=True)
    print(f"Reason:\n{reason}\n", flush=True)
    print("="*40, flush=True)
    sys.exit(1)

def validate_all():
    # 1. Routing
    try:
        route_registry = RouteRegistry("routing/routes.yaml")
    except Exception as e:
        fail("routing/routes.yaml", "YAML Parsing", str(e))
        
    # Check for duplicate routes
    seen_routes = set()
    for route in route_registry.config.routes:
        for method in route.methods:
            key = f"{route.path}:{method}"
            if key in seen_routes:
                fail("routing/routes.yaml", "routes", f"Duplicate route definition for {key}")
            seen_routes.add(key)
            
            if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "ANY"]:
                fail("routing/routes.yaml", "method", f"Invalid HTTP method '{method}' for path {route.path}")

    # 2. Services
    try:
        service_registry = ServiceRegistry("load_balancer/services.yaml")
    except Exception as e:
        fail("load_balancer/services.yaml", "YAML Parsing", str(e))
        
    for route in route_registry.config.routes:
        if route.service not in service_registry.services:
            fail("routing/routes.yaml", "service", f"Route {route.path} references missing service '{route.service}'")
            
    for service_name, service in service_registry.services.items():
        if not service.instances:
            fail("load_balancer/services.yaml", "instances", f"Service '{service_name}' must have at least one instance")

    # 3. Retry
    try:
        retry_config = RetryLoader("config/retry.yaml").config
    except Exception as e:
        fail("config/retry.yaml", "YAML Parsing", str(e))
        
    if retry_config.attempts < 1:
        fail("config/retry.yaml", "attempts", "attempts must be >= 1")
    if retry_config.backoff < 0:
        fail("config/retry.yaml", "backoff", "backoff must be >= 0")

    # 4. Timeout
    try:
        timeout_config = TimeoutLoader("config/timeout.yaml").config
    except Exception as e:
        fail("config/timeout.yaml", "YAML Parsing", str(e))
        
    if timeout_config.connect < 0:
        fail("config/timeout.yaml", "connect", "connect timeout must be >= 0")
    if timeout_config.read < 0:
        fail("config/timeout.yaml", "read", "read timeout must be >= 0")
    if timeout_config.write < 0:
        fail("config/timeout.yaml", "write", "write timeout must be >= 0")

    # 5. Circuit Breaker
    try:
        cb_config = CircuitBreakerLoader("config/circuit_breaker.yaml").config
    except Exception as e:
        fail("config/circuit_breaker.yaml", "YAML Parsing", str(e))
        
    if cb_config.failure_threshold < 1:
        fail("config/circuit_breaker.yaml", "failure_threshold", "failure_threshold must be >= 1")
    if cb_config.success_threshold < 1:
        fail("config/circuit_breaker.yaml", "success_threshold", "success_threshold must be >= 1")
    if cb_config.recovery_timeout < 1:
        fail("config/circuit_breaker.yaml", "recovery_timeout", "recovery_timeout must be >= 1")

    # 6. Cache
    try:
        cache_config = CacheConfigLoader("cache/config.yaml").config
    except Exception as e:
        fail("cache/config.yaml", "YAML Parsing", str(e))
        
    if cache_config.default_ttl <= 0:
        fail("cache/config.yaml", "default_ttl", "default_ttl must be > 0")

    # 7. Rate Limiter
    try:
        rate_limit_config = RateLimitLoader("config/rate_limit.yaml").config
    except Exception as e:
        fail("config/rate_limit.yaml", "YAML Parsing", str(e))
        
    if rate_limit_config.limit <= 0:
        fail("config/rate_limit.yaml", "limit", "limit must be > 0")
    if rate_limit_config.window <= 0:
        fail("config/rate_limit.yaml", "window", "window must be > 0")
