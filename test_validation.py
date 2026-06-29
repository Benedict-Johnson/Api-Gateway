import subprocess
import os

def test_invalid_retry():
    print("\n--- Testing Invalid Retry Config ---")
    original = ""
    with open("config/retry.yaml", "r") as f:
        original = f.read()

    try:
        with open("config/retry.yaml", "w") as f:
            f.write("attempts: 0\nbackoff: -1\n")

        result = subprocess.run(["python", "-c", "from config.validator import validate_all; validate_all()"], capture_output=True, text=True)
        print("Exit code:", result.returncode)
        print("Output:\n", result.stdout)
    finally:
        with open("config/retry.yaml", "w") as f:
            f.write(original)

def test_missing_service():
    print("\n--- Testing Missing Service in Routes ---")
    original = ""
    with open("routing/routes.yaml", "r") as f:
        original = f.read()

    try:
        invalid_yaml = original.replace("service: user-service", "service: missing-service")
        with open("routing/routes.yaml", "w") as f:
            f.write(invalid_yaml)

        result = subprocess.run(["python", "-c", "from config.validator import validate_all; validate_all()"], capture_output=True, text=True)
        print("Exit code:", result.returncode)
        print("Output:\n", result.stdout)
    finally:
        with open("routing/routes.yaml", "w") as f:
            f.write(original)

if __name__ == "__main__":
    test_invalid_retry()
    test_missing_service()
