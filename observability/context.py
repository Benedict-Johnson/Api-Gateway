import contextvars

# Correlation ID for the request
request_id_var = contextvars.ContextVar("request_id", default="-")

# Target service
service_name_var = contextvars.ContextVar("service_name", default="-")

# Cache status (HIT, MISS, BYPASS)
cache_status_var = contextvars.ContextVar("cache_status", default="-")

# Retry count
retry_count_var = contextvars.ContextVar("retry_count", default=0)

# Circuit Breaker state
circuit_state_var = contextvars.ContextVar("circuit_state", default="-")


def get_log_context():
    return {
        "req_id": request_id_var.get(),
        "service": service_name_var.get(),
        "cache": cache_status_var.get(),
        "retries": retry_count_var.get(),
        "circuit": circuit_state_var.get(),
    }
