"""Configuration management for ChatSpy."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration with Pydantic settings."""

    model_config = SettingsConfigDict(
        env_prefix="CHATSPY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # User Settings
    username: Optional[str] = Field(default=None, description="User's display name")
    user_id: Optional[str] = Field(default=None, description="Unique user identifier (UUID)")

    # Network Settings
    discovery_port: int = Field(default=5000, description="Port for mDNS discovery")
    listen_port: int = Field(default=5001, description="Port for incoming P2P connections")
    broadcast_interval: int = Field(default=5, description="Seconds between discovery broadcasts")

    # UI Settings
    theme: str = Field(default="aura", description="UI color theme")
    notification_enabled: bool = Field(default=True, description="Enable desktop notifications")
    sound_enabled: bool = Field(default=False, description="Enable sound notifications")

    # Security Settings
    auto_accept_peers: bool = Field(default=True, description="Automatically accept peer connections")
    key_rotation_days: int = Field(default=0, description="Days before rotating session keys (0=disabled)")

    # Paths
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "chatspy",
        description="Configuration directory"
    )

    @property
    def keys_dir(self) -> Path:
        """Directory for storing cryptographic keys."""
        return self.config_dir / "keys"

    @property
    def private_key_path(self) -> Path:
        """Path to RSA private key file."""
        return self.keys_dir / "private_key.pem"

    @property
    def public_key_path(self) -> Path:
        """Path to RSA public key file."""
        return self.keys_dir / "public_key.pem"

    @property
    def config_file(self) -> Path:
        """Path to TOML config file."""
        return self.config_dir / "config.toml"

    def ensure_directories(self) -> None:
        """Create config and keys directories if they don't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

    def save_to_file(self) -> None:
        """Save current configuration to TOML file."""
        import tomli_w

        self.ensure_directories()

        config_data = {
            "user": {
                "username": self.username,
                "user_id": self.user_id,
            },
            "network": {
                "discovery_port": self.discovery_port,
                "listen_port": self.listen_port,
                "broadcast_interval": self.broadcast_interval,
            },
            "ui": {
                "theme": self.theme,
                "notification_enabled": self.notification_enabled,
                "sound_enabled": self.sound_enabled,
            },
            "security": {
                "auto_accept_peers": self.auto_accept_peers,
                "key_rotation_days": self.key_rotation_days,
            },
        }

        with open(self.config_file, "wb") as f:
            tomli_w.dump(config_data, f)

    @classmethod
    def load_from_file(cls) -> "Config":
        """Load configuration from TOML file if it exists."""
        config_path = Path.home() / ".config" / "chatspy" / "config.toml"

        if not config_path.exists():
            return cls()

        import tomli

        with open(config_path, "rb") as f:
            data = tomli.load(f)

        # Flatten nested structure for Pydantic
        flat_data = {}
        if "user" in data:
            flat_data.update(data["user"])
        if "network" in data:
            flat_data.update(data["network"])
        if "ui" in data:
            flat_data.update(data["ui"])
        if "security" in data:
            flat_data.update(data["security"])

        return cls(**flat_data)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config.load_from_file()
        _config.ensure_directories()
    return _config


def set_config(config: Config) -> None:
    """Set global config instance."""
    global _config
    _config = config
