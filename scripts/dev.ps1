[CmdletBinding()]
param (
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet("up", "down", "rebuild", "logs", "clean", "test", "benchmark", "lint", "format", "health", "help")]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  up        Start Docker containers in background"
    Write-Host "  down      Stop and remove Docker containers"
    Write-Host "  rebuild   Rebuild and start Docker containers"
    Write-Host "  logs      Tail Docker container logs"
    Write-Host "  clean     Remove Python cache and temporary files"
    Write-Host "  test      Run unit and regression test suite inside Docker container"
    Write-Host "  benchmark Run benchmark suite against running gateway"
    Write-Host "  lint      Check codebase quality with ruff"
    Write-Host "  format    Standardize import ordering and format code with isort and black"
    Write-Host "  health    Check live API Gateway health status"
}

switch ($Command) {
    "up" {
        docker compose up -d
    }
    "down" {
        docker compose down
    }
    "rebuild" {
        docker compose up -d --build
    }
    "logs" {
        docker compose logs -f
    }
    "clean" {
        Write-Host "Cleaning cache files..." -ForegroundColor Yellow
        Get-ChildItem -Path . -Include "__pycache__", ".pytest_cache", ".ruff_cache" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Filter "*.pyc" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "Cleaned successfully." -ForegroundColor Green
    }
    "test" {
        docker compose exec -T gateway pytest -v
    }
    "benchmark" {
        if (Get-Command node -ErrorAction SilentlyContinue) {
            node benchmarks/benchmark.js
        } else {
            Write-Host "Node.js not found on host." -ForegroundColor Red
        }
    }
    "lint" {
        python -m ruff check .
    }
    "format" {
        python -m isort .
        python -m black .
    }
    "health" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
            $response | ConvertTo-Json -Depth 5
        } catch {
            Write-Host "Gateway unreachable or error: $_" -ForegroundColor Red
        }
    }
    "help" {
        Show-Help
    }
}
