import os
import subprocess


def get_env(overrides=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    if overrides:
        env.update(overrides)
    return env


def test_invalid_retry():
    print("\n--- Testing Invalid Retry Config ---")
    original = ""
    with open("config/retry.yaml") as f:
        original = f.read()

    try:
        with open("config/retry.yaml", "w") as f:
            f.write("attempts: 0\nbackoff: -1\n")

        result = subprocess.run(
            [
                "python",
                "-c",
                "from config.validator import validate_all; validate_all()",
            ],
            capture_output=True,
            text=True,
            env=get_env(),
        )
        print("Exit code:", result.returncode)
        print("Output:\n", result.stdout)
        assert result.returncode == 1, "Expected exit code 1 for invalid retry config"
    finally:
        with open("config/retry.yaml", "w") as f:
            f.write(original)


def test_missing_service():
    print("\n--- Testing Missing Service in Routes ---")
    original = ""
    with open("routing/routes.yaml") as f:
        original = f.read()

    try:
        invalid_yaml = original.replace(
            "service: user-service", "service: missing-service"
        )
        with open("routing/routes.yaml", "w") as f:
            f.write(invalid_yaml)

        result = subprocess.run(
            [
                "python",
                "-c",
                "from config.validator import validate_all; validate_all()",
            ],
            capture_output=True,
            text=True,
            env=get_env(),
        )
        print("Exit code:", result.returncode)
        print("Output:\n", result.stdout)
        assert (
            result.returncode == 1
        ), "Expected exit code 1 for missing service in routes"
    finally:
        with open("routing/routes.yaml", "w") as f:
            f.write(original)


def test_missing_required_env():
    print("\n--- Testing Missing Required Env Vars ---")
    env = get_env({"JWT_SECRET": ""})
    result = subprocess.run(
        ["python", "-c", "from config.validator import validate_all; validate_all()"],
        capture_output=True,
        text=True,
        env=env,
    )
    print("Exit code:", result.returncode)
    print("Output:\n", result.stdout)
    assert result.returncode == 1, "Expected exit code 1 for empty JWT_SECRET"
    assert "CONFIG VALIDATION FAILED" in result.stdout


def test_placeholder_env():
    print("\n--- Testing Placeholder Env Vars ('change-me') ---")
    env = get_env({"API_KEY_SECRET": "change-me"})
    result = subprocess.run(
        ["python", "-c", "from config.validator import validate_all; validate_all()"],
        capture_output=True,
        text=True,
        env=env,
    )
    print("Exit code:", result.returncode)
    print("Output:\n", result.stdout)
    assert result.returncode == 1, "Expected exit code 1 for placeholder API_KEY_SECRET"
    assert "CONFIG VALIDATION FAILED" in result.stdout


if __name__ == "__main__":
    test_invalid_retry()
    test_missing_service()
    test_missing_required_env()
    test_placeholder_env()
    print("\nAll validation tests passed successfully!")
