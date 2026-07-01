<div align="center">

# 🌌 Enterprise Python API Gateway v1.0.0

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-Latest-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Latest-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Latest-F46800.svg?logo=grafana&logoColor=white)](https://grafana.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

A high-performance, asynchronous, production-grade API Gateway built from scratch in Python using the modern ASGI ecosystem (FastAPI, Starlette, Uvicorn, and HTTPX). Designed to serve as a centralized ingress controller for distributed microservice architectures, providing dynamic routing, database-backed security, intelligent load balancing, resilience engineering, and comprehensive real-time observability.

</div>

---

## 1. Project Overview

In modern microservice architectures, allowing client applications to communicate directly with dozens of independent backend services introduces critical operational bottlenecks:
- **Tight Coupling:** Clients must hardcode internal network hostnames, ports, and service topologies.
- **Redundant Engineering:** Every microservice must independently implement Cross-Origin Resource Sharing (CORS), rate limiting policies, token validation, and logging.
- **Security Vulnerabilities:** Exposing raw microservices to the public internet expands the attack surface.
- **Performance Degradation:** High network latency caused by chatty client-to-service roundtrips.

The **Enterprise Python API Gateway** solves these challenges by acting as a single, hardened reverse proxy ingress point. It abstracts the downstream microservice ecosystem behind a unified RESTful interface, intercepting all HTTP traffic to enforce strict security policies, execute high-speed Redis caching, dynamically balance loads across healthy instances, and protect internal systems from cascading overload using stateful circuit breakers.

### Docker Containers Running

The gateway is built from the ground up for containerized deployment, orchestrating the proxy engine, Redis cache, PostgreSQL storage layer, mock backend services, Prometheus metrics collector, and Grafana visualization dashboards via Docker Compose.

![Docker Containers Running](screenshots/docker_containers_running.png)
*Figure 1: Fully containerized microservices architecture running seamlessly via Docker Compose, including the API Gateway, backend microservices, Redis cache, PostgreSQL database, Prometheus metrics engine, and Grafana dashboard.*

### Gateway Root Endpoint

At runtime, the gateway exposes a clean management and introspection interface that reports active versioning, operational state, and feature toggles.

![Gateway Root Endpoint](screenshots/root_endpoint.png)
*Figure 2: The Gateway Root Endpoint returning live system status, version information, and active security feature flags.*

---

## 2. Features

The gateway implements a full suite of production-ready features organized into functional domains:

| Feature Category | Implemented Capabilities |
| :--- | :--- |
| **Reverse Proxy & Routing** | Asynchronous non-blocking HTTP proxying via `httpx.AsyncClient`, declarative YAML-based dynamic route configuration, path parameter matching, and header propagation. |
| **Authentication & Security** | Cryptographic JWT verification, database-backed API key management (`X-API-Key`) with bcrypt hashing, Role-Based Access Control (RBAC), and automated request validation. |
| **Traffic Control & Caching** | High-performance Redis-backed caching with MD5 key hashing and configurable TTLs, multi-algorithm rate limiting (Leaky Bucket, Token Bucket, Fixed/Sliding Window) executed atomically via Redis Lua scripts. |
| **Load Balancing & Discovery** | Active background health checking, automated service registry (`/discovery`), dynamic Round Robin, Weighted Round Robin, and real-time Least Connections load balancing. |
| **Resilience Engineering** | Thread-safe Circuit Breakers (CLOSED, OPEN, HALF-OPEN states), exponential backoff retries with jitter for transient failures, and strict per-route timeout enforcement. |
| **Observability & Logging** | Native Prometheus metrics exporter (`/metrics`), Grafana dashboards, structured JSON audit logging with request ID tracing, and real-time liveness/readiness probes (`/health`, `/live`, `/ready`). |
| **Production Release Engineering** | Zero-downtime graceful shutdown with connection pool draining, strict startup configuration validation via `pydantic-settings`, and HTTP security headers (HSTS, CSP, X-Frame-Options). |

---

## 3. Architecture

The API Gateway is engineered as an asynchronous, multi-layered pipeline. When an HTTP request enters the gateway, it traverses an ordered sequence of middleware filters before reaching the core routing engine and downstream infrastructure.

```mermaid
flowchart TD
    Client([Client / API Consumer]) -->|HTTP / HTTPS| MW[Middleware Layer]
    
    subgraph MW [Ordered Middleware Pipeline]
        M1[1. Security Headers Middleware] --> M2[2. Audit Logging & Request ID]
        M2 --> M3[3. Request Validation]
        M3 --> M4[4. Rate Limiting Engine]
        M4 --> M5[5. Authentication & RBAC]
    end
    
    MW --> Gateway[Core Gateway Engine]
    
    Gateway --> Cache{Redis Cache Check}
    Cache -->|Cache HIT| Client
    Cache -->|Cache MISS| LB[Least Connections Load Balancer]
    
    LB --> Discovery[Service Discovery Registry]
    Discovery --> CB[Circuit Breaker & Retry Engine]
    CB -->|Proxy Request| Backend[Downstream Microservices]
    
    Gateway <-->|Store & Verify API Keys| PG[(PostgreSQL Database)]
    Gateway <-->|Rate Limit Tokens & Cached Responses| Redis[(Redis Cache)]
    Gateway -->|Export Time-Series Metrics| Prom[Prometheus Server]
    Prom --> Graf[Grafana Monitoring Dashboards]
```

---

## 4. Request Lifecycle

Every incoming client request is systematically processed through an ordered chain of responsibility:

1. **Security Headers Middleware**: Immediately injects hardened HTTP response headers (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`) to mitigate Cross-Site Scripting (XSS), clickjacking, and MIME-sniffing vulnerabilities.
2. **Audit Logging & Request ID Middleware**: Generates a universally unique identifier (`X-Request-ID`) if not supplied by the client, attaches it to the request state, records exact arrival timestamps, and emits structured JSON audit logs capturing client metadata, IP addresses, and execution duration.
3. **Request Validation Middleware**: Inspects incoming payload lengths against configured thresholds and verifies content-type integrity to prevent Denial-of-Service (DoS) memory exhaustion and malformed payload injection.
4. **Rate Limiting Middleware**: Interrogates the Redis cluster using atomic Lua scripts to evaluate traffic quotas under the configured algorithm (e.g., Leaky Bucket). If the client quota is exceeded, it immediately rejects the request with HTTP `429 Too Many Requests` while populating standard rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).
5. **Authentication & RBAC Middleware**: Extracts credentials from bearer tokens or `X-API-Key` headers. It validates JWT signatures or queries PostgreSQL to verify bcrypt-hashed API keys, checks active revocation timestamps, increments usage statistics, and verifies whether the authenticated identity possesses the necessary RBAC role (`admin`, `service`, `user`) for the requested route.
6. **Core Proxy & Caching Engine**: Checks Redis for a valid cached response matching the request method and path MD5 hash. On a cache hit, the payload is returned immediately. On a cache miss, the Least Connections load balancer evaluates real-time connection pools to select the optimal downstream service instance, executing the proxied call through circuit breaker protection and exponential backoff retry policies.

---

## 5. Folder Structure

The repository is modularly structured following enterprise Python domain-driven design principles:

```text
api-gateway/
├── audit/              # Structured JSON audit logging and security event tracking
├── auth/               # JWT authentication, API key manager, RBAC policies, and admin router (/admin/api-keys)
├── cache/              # Redis caching engine, MD5 hash key generation, and TTL management
├── circuit_breaker/    # Thread-safe circuit breaker state machine (CLOSED, OPEN, HALF-OPEN)
├── config/             # Centralized pydantic-settings configuration loading and fail-fast startup validation
├── database/           # SQLAlchemy ORM engine, declarative models, and PostgreSQL schema initialization
├── discovery/          # Dynamic service discovery registry, background health checkers, and /discovery endpoints
├── docker/             # Dockerfiles and container configurations for gateway and mock services (service-a, service-b)
├── gateway/            # Core FastAPI application initialization, lifespan event handlers, and exception handlers
├── load_balancer/      # Least Connections, Round Robin, and Weighted Round Robin load balancing algorithms
├── observability/      # Native Prometheus metrics exporter and Grafana dashboard integration
├── proxy/              # High-performance asynchronous HTTP reverse proxy engine using httpx.AsyncClient
├── rate_limiter/       # Multi-algorithm rate limiting manager with atomic Redis Lua script execution
├── resilience/         # Exponential backoff retry policies with jitter and per-route timeout enforcement
├── routing/            # Declarative YAML route parser, path matcher, and downstream destination resolution
├── screenshots/        # Verified production and dashboard screenshots for documentation
└── tests/              # Complete pytest regression test suite, unit tests, and automated smoke testing script
```

---

## 6. Technology Stack

The project relies on proven, industry-standard technologies chosen for performance, reliability, and asynchronous capabilities:

| Layer | Technology | Purpose & Justification |
| :--- | :--- | :--- |
| **Core Framework** | Python 3.12, FastAPI, Starlette | Modern, typed ASGI web framework providing asynchronous execution, OpenAPI auto-generation, and high concurrency. |
| **Proxy Engine** | HTTPX (`AsyncClient`) | High-speed async HTTP client utilizing connection pooling and non-blocking I/O for reverse proxying. |
| **Data Storage** | PostgreSQL 16, SQLAlchemy ORM | Relational database engine storing persistent API keys, role assignments, revocation timestamps, and audit history. |
| **Caching & Traffic** | Redis 7, `redis-py` | In-memory data store powering atomic Lua-based rate limiting quotas and sub-millisecond HTTP response caching. |
| **Security & Crypto** | Bcrypt, PyJWT, Pydantic v2 | Cryptographic hashing of secrets, JSON Web Token verification, and strict data validation schemas. |
| **Observability** | Prometheus, Grafana | Time-series metrics scraping and visual dashboard monitoring for real-time gateway telemetry. |
| **DevOps & Testing** | Docker, Docker Compose, Pytest | Containerized orchestration, reproducible environment isolation, and comprehensive regression test automation. |

---

## 7. Installation

### Prerequisites
- **Docker & Docker Compose**: Ensure Docker Engine v24+ and Docker Compose v2+ are installed.
- **Python 3.12+**: Required only if running local test suites outside container environments.

### Step 1: Clone the Repository
```bash
git clone https://github.com/Benedict-Johnson/Api-Gateway.git
cd Api-Gateway
```

### Step 2: Configure Environment Variables
Copy the example configuration template to create your local `.env` file:
```bash
cp .env.example .env
```
*(Note: Do not modify `DEMO_MODE=false` unless generating local screenshots).*

### Step 3: Launch Docker Environment
Build and start the entire multi-container infrastructure in detached mode:
```bash
docker compose up -d --build
```

### Step 4: Verify Deployment
Check that all services are online and operational:
```bash
docker compose ps
```
The API Gateway is now running and accepting traffic at `http://localhost:8000`.

---

## 8. Docker Setup

The project provides a self-contained infrastructure managed via `docker-compose.yml`. It spins up seven interconnected containers over an isolated Docker bridge network:

1. **`gateway` (Port 8000)**: The core API Gateway reverse proxy engine built from `docker/gateway/Dockerfile`.
2. **`service-a` & `service-b`**: Mock downstream microservices simulating business logic (`/orders`, `/users`, `/billing`).
3. **`redis` (Port 6379)**: Dedicated Redis server for rate limiting token buckets and HTTP response caching.
4. **`postgres` (Port 5432)**: PostgreSQL database container initialized with persistent volumes for API key storage.
5. **`prometheus` (Port 9090)**: Time-series database actively scraping the gateway's `/metrics` endpoint every 5 seconds.
6. **`grafana` (Port 3000)**: Visualization server pre-provisioned with data sources and custom latency dashboards.

---

## 9. Environment Variables

The gateway enforces strict startup configuration validation using `pydantic-settings`. Every environment variable documented in `.env.example` must be supplied. If required secrets are missing or contain placeholder values in production, the application fails fast with a descriptive error.

| Environment Variable | Default Value / Example | Description & Operational Notes |
| :--- | :--- | :--- |
| `JWT_SECRET` | `change-me` | Secret key used for cryptographic signing and verification of JWT bearer tokens. **Must be overridden in production.** |
| `API_KEY_SECRET` | `change-me` | Internal secret key used for administrative service authentication. **Must be overridden in production.** |
| `REDIS_HOST` | `redis` | Hostname of the Redis server (`redis` within Docker network, `localhost` for local testing). |
| `REDIS_PORT` | `6379` | Port number on which the Redis server is listening. |
| `REDIS_PASSWORD` | *(empty)* | Optional password for Redis authentication if ACLs are enabled. |
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/gateway` | Fully qualified PostgreSQL SQLAlchemy connection string. |
| `ENVIRONMENT` | `development` | Runtime environment execution context (`development`, `staging`, `production`). |
| `LOG_LEVEL` | `INFO` | Verbosity level for structured JSON logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `DEMO_MODE` | `false` | **Documentation Flag**: Temporarily bypasses auth and rate limits for screenshot generation. **Must be `false` in production.** |
| `ENABLE_TLS` | `false` | Boolean toggle indicating whether internal TLS encryption termination is active. |

> [!WARNING]
> **Security Notice:** Never commit your production `.env` file to version control. Ensure `.env` is listed in your `.gitignore` file at all times.

---

## 10. API Overview

The gateway exposes distinct endpoint categories for management, observability, and downstream reverse proxying:

### System & Health Endpoints
- `GET /`: Returns core gateway version metadata, status, and active feature flags.
- `GET /health`: Comprehensive health diagnostic reporting real-time status of PostgreSQL, Redis, service discovery, and memory.
- `GET /live`: Lightweight Kubernetes liveness probe endpoint returning `200 OK` if the async event loop is responsive.
- `GET /ready`: Kubernetes readiness probe verifying active connectivity to backend dependencies before accepting traffic.

### Administrative API Key Management (Requires Admin Role)
- `POST /admin/api-keys`: Creates a new database-backed API key with designated RBAC role (`admin`, `service`, `user`). Returns plaintext key once.
- `GET /admin/api-keys`: Lists all active and revoked API keys with usage statistics and audit metadata.
- `DELETE /admin/api-keys/{key_id}`: Soft-revokes an existing API key, disabling access while preserving audit history.

### Service Discovery & Routing
- `GET /discovery`: Returns the complete real-time registry of all known downstream microservices and their active health states.
- `GET /discovery/{service_name}`: Inspects specific instance details, connection pools, and error rates for a named service.
- `ANY /orders/*`, `/users/*`, `/billing/*`: Downstream proxied routes forwarded to healthy microservice instances based on YAML routing rules.

### Observability & Documentation
- `GET /metrics`: Native Prometheus export endpoint exposing detailed counters and histograms.
- `GET /docs`: Interactive Swagger UI documentation (OpenAPI specification).
- `GET /redoc`: Alternative ReDoc interactive API documentation.

---

## 11. Security

Security is embedded into every layer of the API Gateway pipeline, defending backend systems against unauthorized access, payload attacks, and data leakage.

### PostgreSQL API Keys & RBAC

Unlike static configuration files, the gateway implements dynamic, database-backed API key management using PostgreSQL and SQLAlchemy. When an administrative key is generated, its secret is one-way hashed using **bcrypt** before persistence; plaintext keys are never stored.

Each API key is assigned an RBAC role (`admin`, `service`, `user`) that dictates route accessibility. When a key is revoked via API, the system performs a **soft deletion** by setting `active = False` and stamping `revoked_at` with the current UTC timestamp. Every successful authentication increments the `usage_count` and updates `last_used`, providing complete auditability.

![PostgreSQL API Keys Database](screenshots/postgreSQL.png)
*Figure 3: Database-backed API Key management stored in PostgreSQL, featuring bcrypt hashed secrets, role assignments, active flags, soft revocation timestamps, and real-time usage statistics.*

### Security Headers & Request Validation
The gateway automatically hardens HTTP responses by injecting defensive security headers:
- `Strict-Transport-Security (HSTS)`: Enforces secure HTTPS connections over a 1-year duration.
- `Content-Security-Policy (CSP)`: Restricts unauthorized script and stylesheet execution (`default-src 'self'`).
- `X-Frame-Options: DENY`: Prevents UI redressing and clickjacking attacks.
- `X-Content-Type-Options: nosniff`: Prevents browsers from MIME-sniffing away from declared content types.

Furthermore, the Request Validation Middleware rejects oversized payloads and malformed syntax before consuming downstream network bandwidth.

---

## 12. Resilience

To guarantee high availability in distributed environments, the gateway incorporates comprehensive resilience engineering patterns designed to survive partial system degradation.

### Thread-Safe Circuit Breakers

When a downstream microservice experiences latency spikes or database lockups, repeatedly forwarding requests causes cascading failures across the entire network. The gateway protects downstream infrastructure using a stateful Circuit Breaker pattern:
1. **CLOSED (Normal Operation)**: Traffic flows freely. If downstream error rates exceed configured thresholds (e.g., 5 consecutive failures), the circuit trips.
2. **OPEN (Fail-Fast Mode)**: The gateway immediately rejects incoming requests with HTTP `503 Service Unavailable` without waiting for network timeouts, allowing the failing backend service time to recover.
3. **HALF-OPEN (Recovery Testing)**: After a configurable cooldown period (e.g., 30 seconds), the circuit allows a limited number of test requests through. If successful, the circuit resets to CLOSED; if failures persist, it reverts immediately to OPEN.

### Circuit Breaker Logs

The following structured logs demonstrate the gateway detecting downstream anomalies, tripping the circuit breaker to OPEN state, and managing automated recovery:

![Circuit Breaker Logs Part 1](screenshots/circuit_breaker_logs_pt1.png)
*Figure 4: Structured logs demonstrating the Circuit Breaker monitoring downstream failures and transitioning from CLOSED to OPEN state to protect backend microservices.*

![Circuit Breaker Logs Part 2](screenshots/circuit_breaker_logs_pt2.png)
*Figure 5: Circuit Breaker entering HALF-OPEN state to test downstream recovery, and returning to CLOSED state once service health is restored.*

### Exponential Backoff Retries & Graceful Shutdown
For transient network glitches, the gateway retries failed requests using exponential backoff with randomized jitter to prevent thundering herd problems. During container termination (`SIGTERM` / `SIGINT`), the Lifespan event handler executes a graceful shutdown: it stops accepting new requests, allows active requests to finish draining, and cleanly closes all asynchronous PostgreSQL and Redis connection pools.

---

## 13. Caching

To minimize latency and reduce database contention on downstream services, the gateway integrates high-speed Redis caching.

### Cache MISS vs. Cache HIT Execution

When a GET request arrives for a cache-enabled route, the gateway computes a deterministic MD5 hash of the URL path and query parameters.
- **Cache MISS**: If no entry exists in Redis, the request is proxied to the downstream service. The response is returned to the client and simultaneously stored asynchronously in Redis with a configurable Time-To-Live (TTL).
- **Cache HIT**: Subsequent requests for the same URI are served directly from Redis memory in sub-millisecond latency, bypassing the load balancer and backend microservice entirely.

![Redis Cache MISS](screenshots/cache_MISS.png)
*Figure 6: Request execution logging a Cache MISS, forwarding the request to the backend microservice via least-connections load balancing and storing the response in Redis.*

![Redis Cache HIT](screenshots/cache_HIT.png)
*Figure 7: Subsequent request execution logging an instant Cache HIT, serving the response directly from Redis in sub-millisecond latency without contacting downstream services.*

---

## 14. Health Monitoring

Continuous health monitoring is essential for Kubernetes and container orchestration platforms. The gateway exposes granular health endpoints that perform active dependency probing.

### Comprehensive Health Diagnostic Endpoint

The `/health` endpoint interrogates the underlying infrastructure in real time, verifying PostgreSQL query responsiveness, Redis ping latency, internal memory consumption, and active service discovery registries.

![Comprehensive Health Monitoring Endpoint](screenshots/health.png)
*Figure 8: Comprehensive health monitoring endpoint (`/health`) displaying real-time connectivity status for Redis, PostgreSQL, service discovery registries, and memory utilization.*

---

## 15. Observability

Observability is a first-class citizen in the API Gateway. The application instruments every request with structured JSON logs and exports native Prometheus time-series metrics.

### Grafana Dashboards & Latency Monitoring

Pre-provisioned Grafana dashboards connect directly to the Prometheus data source, providing operations teams with visual telemetry over traffic throughput, error distributions, active connection pools, and P50/P95/P99 latency percentiles.

![Grafana Dashboard Overview](screenshots/grafana_dashboard.png)
*Figure 9: Comprehensive Grafana monitoring dashboard visualizing API Gateway throughput, HTTP status code distributions, active connection counts, and system health.*

![Grafana Latency Panel](screenshots/grafana_latency_panel.png)
*Figure 10: Granular Grafana latency panel tracking P50, P95, and P99 response times across proxied microservice endpoints.*

### Prometheus Time-Series Metrics

The integrated Prometheus collector scrapes the gateway's `/metrics` endpoint, recording histograms for request durations and counters for circuit breaker trips, cache hit ratios, and rate limit rejections.

![Prometheus Metrics Server](screenshots/prometheus.png)
*Figure 11: Prometheus monitoring server collecting real-time time-series metrics from the API Gateway exporter.*

![Prometheus Metrics Endpoint](screenshots/metrics.png)
*Figure 12: Native Prometheus `/metrics` endpoint exposing detailed counters, gauges, and histograms for HTTP traffic, cache performance, and circuit breaker states.*

---

## 16. Testing

The gateway includes a rigorous, multi-layered testing suite designed to ensure zero regressions across architectural refactors and security enhancements.

### Automated Smoke Test Suite

The project includes a standalone end-to-end verification script (`tests/smoke_test.py`) that executes against a live gateway instance. It systematically verifies liveness probes, Redis cache readiness, comprehensive health diagnostics, dynamic service discovery, authentication rejection, and rate limiter enforcement.

![Automated Smoke Test Suite](screenshots/smoke_test.png)
*Figure 13: Execution of the automated end-to-end Smoke Test suite verifying gateway liveness, Redis cache readiness, health checks, service discovery, rate limiting, and authentication security.*
*(Note: Screenshot displays `smoke_test.png` demonstrating automated verification).*

### Full Pytest Regression Suite
The repository maintains a comprehensive 12-module pytest regression suite covering unit and integration testing across all gateway components:
```bash
# Execute the complete regression suite inside Docker
docker compose exec -T gateway pytest tests/ -v
```
The regression suite verifies caching managers, least-connections load balancers, database API key lifecycles, RBAC administrative routers, security headers, request validation, and structured audit logging with **100% pass rates**.

---

## 17. Documentation Mode

To facilitate UI demonstrations, architectural review, and README screenshot generation without triggering security rejections or rate limit blocks, the gateway includes a centralized temporary **Documentation Mode**.

### Enabling Documentation Mode
When `DEMO_MODE=true` is set in the environment configuration:
- **Authentication & RBAC Bypassed**: All protected endpoints (`/admin/api-keys`, `/orders`, `/docs`, etc.) become accessible without requiring API keys or JWT headers.
- **Rate Limiting Disabled**: Quotas are bypassed with dummy headers (`X-RateLimit-Limit: 999999`), allowing rapid UI navigation and automated screenshot capture.
- **Production Logic Intact**: Reverse proxy routing, caching, load balancing, circuit breakers, and observability remain fully functional.

> [!CAUTION]
> **Production Safety Warning:** `DEMO_MODE=true` exists strictly for local demonstration and screenshot generation. **You must never enable Documentation Mode in staging or production environments!** The default value in `.env.example` is strictly set to `DEMO_MODE=false`.

---

## 18. Future Improvements

As the enterprise gateway continues to evolve, the following enhancements are planned for future major releases:
1. **Dynamic Administrative Web UI**: A React/Next.js dashboard for real-time visual management of routing YAML rules, rate limit quotas, and RBAC role assignments without restarting containers.
2. **Distributed OpenTelemetry (OTel) Tracing**: Integration with Jaeger and Zipkin for distributed W3C trace context propagation across multi-hop microservice topologies.
3. **Advanced Canary & Blue-Green Deployment Routing**: Weighted header-based and cookie-based traffic splitting to support zero-risk progressive service rollouts.
4. **WebSocket & gRPC Proxying**: Extending the async proxy engine to support bidirectional WebSocket tunneling and HTTP/2 gRPC protocol streaming.
5. **Global Redis Cluster Rate Limiting**: Multi-region rate limit synchronization across geographically distributed Redis Cluster shards.

---

## 19. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
<div align="center">
<b>Engineered with precision for advanced distributed systems and high-performance asynchronous web architectures.</b>
</div>
