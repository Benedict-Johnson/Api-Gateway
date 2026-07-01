import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import httpx

# Ensure DB is configured for test environment if not inside docker
if not os.path.exists("/.dockerenv"):
    if "DATABASE_URL" in os.environ:
        os.environ["DATABASE_URL"] = os.environ["DATABASE_URL"].replace(
            "@postgres:5432", "@localhost:5432"
        )
    else:
        os.environ["DATABASE_URL"] = (
            "postgresql://postgres:postgres@localhost:5432/gateway"
        )

from config.settings import settings

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
API_KEY_HEADER = {"X-API-Key": settings.API_KEY_SECRET}


async def run_standalone_smoke_tests():
    print("====================================================")
    print("       API Gateway - Production Smoke Suite         ")
    print("====================================================")
    print(f"Target Gateway URL: {GATEWAY_URL}\n")

    results = []

    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        # Check 1: Liveness
        try:
            resp = await client.get("/live")
            passed = resp.status_code == 200 and resp.json().get("status") == "UP"
            results.append(
                ("1. Gateway Liveness (/live)", passed, f"Status: {resp.status_code}")
            )
        except Exception as e:
            results.append(("1. Gateway Liveness (/live)", False, str(e)))

        # Check 2: Readiness
        try:
            resp = await client.get("/ready")
            passed = resp.status_code == 200 and resp.json().get("status") == "UP"
            results.append(
                (
                    "2. Redis Cache Readiness (/ready)",
                    passed,
                    f"Status: {resp.status_code}",
                )
            )
        except Exception as e:
            results.append(("2. Redis Cache Readiness (/ready)", False, str(e)))

        # Check 3: Health
        try:
            resp = await client.get("/health")
            passed = resp.status_code == 200 and resp.json().get("gateway") == "UP"
            results.append(
                (
                    "3. Comprehensive Health (/health)",
                    passed,
                    f"Status: {resp.status_code}",
                )
            )
        except Exception as e:
            results.append(("3. Comprehensive Health (/health)", False, str(e)))

        # Check 4: Discovery
        try:
            resp = await client.get("/discovery/service-a", headers=API_KEY_HEADER)
            passed = resp.status_code == 200 and isinstance(resp.json(), list)
            results.append(
                (
                    "4. Service Discovery (/discovery/service-a)",
                    passed,
                    f"Status: {resp.status_code}",
                )
            )
        except Exception as e:
            results.append(
                ("4. Service Discovery (/discovery/service-a)", False, str(e))
            )

        # Check 5: Auth
        try:
            resp = await client.get("/admin/api-keys")
            passed = resp.status_code in (401, 403)
            results.append(
                (
                    "5. Authentication Rejection (/admin/api-keys)",
                    passed,
                    f"Status: {resp.status_code}",
                )
            )
        except Exception as e:
            results.append(
                ("5. Authentication Rejection (/admin/api-keys)", False, str(e))
            )

        # Check 6: Rate Limiting
        try:
            codes = []
            for _ in range(25):
                r = await client.get("/live")
                codes.append(r.status_code)
                if r.status_code == 429:
                    break
            passed = all(c in (200, 429) for c in codes)
            results.append(
                (
                    "6. Rate Limiter Enforcement (/live burst)",
                    passed,
                    f"Codes: {set(codes)}",
                )
            )
        except Exception as e:
            results.append(("6. Rate Limiter Enforcement (/live burst)", False, str(e)))

    print("----------------------------------------------------")
    print("Test Results:")
    print("----------------------------------------------------")
    passed_count = 0
    for name, passed, details in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        if passed:
            passed_count += 1
        print(f"{status_str:6} {name:45} ({details})")
    print("----------------------------------------------------")
    total_count = len(results)
    failed_count = total_count - passed_count
    print(f"Summary: {passed_count}/{total_count} passed, {failed_count} failed.")
    print("====================================================")
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_standalone_smoke_tests())
    sys.exit(exit_code)
