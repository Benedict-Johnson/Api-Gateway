from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Authentication
    JWT_SECRET: str = Field(
        "change-me", description="Secret key for signing and verifying JWT tokens"
    )
    API_KEY_SECRET: str = Field(
        "change-me",
        description="Secret key for internal service-to-gateway API authentication",
    )

    # Redis
    REDIS_HOST: str = Field("localhost", description="Redis host address")
    REDIS_PORT: int = Field(6379, description="Redis port number")
    REDIS_PASSWORD: str | None = Field(
        None, description="Redis password if authentication is enabled"
    )

    # Database
    DATABASE_URL: str = Field(
        "postgresql://postgres:postgres@postgres:5432/gateway",
        description="Database connection URL",
    )

    # Gateway
    ENVIRONMENT: str = Field(
        "development",
        description="Operating environment (development, staging, production)",
    )
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # Security
    ENABLE_TLS: bool = Field(False, description="Whether TLS is enabled")
    CERT_PATH: str = Field("cert.pem", description="Path to SSL certificate file")
    KEY_PATH: str = Field("key.pem", description="Path to SSL private key file")

    SECURITY_HEADERS_ENABLED: bool = Field(
        True, description="Whether security headers are injected"
    )
    HSTS_HEADER: str = Field(
        "max-age=31536000; includeSubDomains",
        description="Strict-Transport-Security header value",
    )
    X_FRAME_OPTIONS_HEADER: str = Field(
        "DENY", description="X-Frame-Options header value"
    )
    X_CONTENT_TYPE_OPTIONS_HEADER: str = Field(
        "nosniff", description="X-Content-Type-Options header value"
    )
    REFERRER_POLICY_HEADER: str = Field(
        "strict-origin-when-cross-origin", description="Referrer-Policy header value"
    )
    PERMISSIONS_POLICY_HEADER: str = Field(
        "geolocation=(), microphone=(), camera=()",
        description="Permissions-Policy header value",
    )
    CONTENT_SECURITY_POLICY_HEADER: str = Field(
        "default-src 'self'", description="Content-Security-Policy header value"
    )

    def validate_startup(self):
        """
        Validates required configuration at startup.
        If required values are missing or invalid, raises ValueError to fail fast.
        """
        errors = []

        if (
            not self.JWT_SECRET
            or self.JWT_SECRET.strip() == ""
            or self.JWT_SECRET == "change-me"
        ):
            errors.append(
                "JWT_SECRET must be set and cannot be empty or default placeholder ('change-me')"
            )

        if (
            not self.API_KEY_SECRET
            or self.API_KEY_SECRET.strip() == ""
            or self.API_KEY_SECRET == "change-me"
        ):
            errors.append(
                "API_KEY_SECRET must be set and cannot be empty or default placeholder ('change-me')"
            )

        if self.REDIS_PORT < 1 or self.REDIS_PORT > 65535:
            errors.append(
                f"REDIS_PORT must be between 1 and 65535, got {self.REDIS_PORT}"
            )

        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(
                f"LOG_LEVEL must be one of {valid_log_levels}, got '{self.LOG_LEVEL}'"
            )

        if not self.DATABASE_URL or self.DATABASE_URL.strip() == "":
            errors.append("DATABASE_URL must be set and cannot be empty")

        if errors:
            raise ValueError("\n".join(errors))


# Expose a single module-level singleton instance
settings = Settings()
