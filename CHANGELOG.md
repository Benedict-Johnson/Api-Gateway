# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-01

### Added
- **Core Reverse Proxy & Routing**
  - High-performance asynchronous reverse proxy using `httpx.AsyncClient`.
  - Dynamic route matching and forwarding to backend microservices (`service-a`, `service-b`, `internal-service`).
  - Support for multi-path routing and custom header propagation.

- **Production Security & Authentication (Phase 9)**
  - Database-backed API Key management using PostgreSQL and SQLAlchemy ORM (`auth/api_key_service.py`).
  - Secure API Key storage using Bcrypt hashing (`passlib`); plaintext keys are never stored.
  - Role-Based Access Control (RBAC) supporting `admin`, `service`, and `dev` roles.
  - API Key Revocation and Soft Deletion tracking via nullable `revoked_at` timestamp.
  - Usage tracking statistics: incremental `usage_count` and `last_used` timestamps.
  - Administrative REST API endpoints under `/admin/api-keys` for key creation, listing, and revocation.
  - JWT Validation and Bearer Token authentication support.
  - Security Headers Middleware injecting HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and Content-Security-Policy.
  - Request Validation Middleware enforcing URI length limits (414), Header size limits (431), Payload size limits (413), and Content-Type validation (415).

- **Traffic Management & Resilience**
  - Distributed Token Bucket Rate Limiter backed by Redis (`rate_limiter/`).
  - Dynamic Service Discovery (`load_balancer/discovery/`) with heartbeat registration and automatic deregistration of unhealthy nodes.
  - Load Balancing algorithms supporting Round-Robin and Least-Connections routing strategies.
  - Circuit Breaker pattern implementation with Closed, Open, and Half-Open states to prevent cascading failures.
  - Configurable request Retry and Timeout mechanisms for downstream service interactions.
  - Redis Cache Manager providing high-speed caching for idempotent GET requests.

- **Observability & Monitoring**
  - Standardized JSON Structured Audit Logging (`audit/logger.py`) recording critical authentication and administrative events (`AUTH_SUCCESS`, `AUTH_FAILURE`, `API_KEY_CREATED`, `API_KEY_REVOKED`, `ADMIN_ACCESS`).
  - Prometheus metrics exporter exposing latency histograms, request counters, and error rate metrics at `/metrics`.
  - Pre-configured Grafana dashboards and Prometheus scraping configurations.
  - Comprehensive health check probes:
    - `/live`: Lightweight liveness probe verifying gateway process responsiveness.
    - `/ready`: Readiness probe checking Redis cache connectivity and database readiness.
    - `/health`: Comprehensive diagnostics reporting subsystem status across Database, Redis, and Discovered Services.

- **Release Engineering & Developer Experience (Phase 10)**
  - Centralized type-safe configuration management using Pydantic Settings (`config/settings.py`) with environment variable validation at startup and `.env` / `.env.example` templates.
  - Single-source-of-truth configuration singleton pattern (`settings = Settings()`).
  - Standardized Python package structure ensuring all modules contain `__init__.py`.
  - Comprehensive automated smoke test suite (`tests/smoke_test.py`) with standalone async HTTP validation and clean CLI reporting.
  - Root `Makefile` and PowerShell automation (`scripts/dev.ps1`) for building, testing, linting, formatting, and running the containerized stack.
  - Code formatting and linting standards configured in `pyproject.toml` using `black`, `isort`, and `ruff`.
  - Rich OpenAPI 3.0 / Swagger UI documentation at `/docs` with detailed endpoint summaries, descriptions, request/response schemas, and error examples.

### Changed
- Refactored API Key storage from static YAML configuration files (`keys.yaml`) to dynamic PostgreSQL tables without breaking existing authentication workflows.
- Replaced direct `os.getenv()` calls across the codebase with type-safe properties on the centralized `settings` singleton.
- Standardized error response payloads across all middleware and routing layers to return consistent JSON error structures.

### Removed
- Dead code, unused imports, commented-out code blocks, and obsolete static key configuration logic during repository cleanup.
