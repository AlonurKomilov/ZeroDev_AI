"""
Secrets Management Service

This module provides a centralized service for managing secrets, such as API keys,
database credentials, and other sensitive data. It is designed to integrate with
a production-grade secrets management system like HashiCorp Vault.
"""

import os
from functools import lru_cache

import hvac
from backend.core.settings import settings


class SecretsManager:
    """
    A secrets manager that mimics fetching secrets from a secure vault.
    In a real implementation, this class would contain logic to connect to
    HashiCorp Vault, AWS Secrets Manager, or another secrets backend.
    """

    def get_secret(self, secret_name: str) -> str:
        raise NotImplementedError


class VaultSecretsManager(SecretsManager):
    """
    A secrets manager that fetches secrets from HashiCorp Vault.
    """

    def __init__(self, vault_addr: str, vault_token: str):
        self.client = hvac.Client(url=vault_addr, token=vault_token)
        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed")

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieves a secret by its name from the vault.
        The secret is assumed to be in a KV v2 secret engine at the path 'zerodev'.
        """
        response = self.client.secrets.kv.v2.read_secret_version(
            path="zerodev",
        )
        return response["data"]["data"].get(secret_name)


class MockSecretsManager(SecretsManager):
    """
    A simulated secrets manager for local development and testing.
    """

    def __init__(self):
        self._vault = {
            "OPENAI_API_KEY": "mock_openai_api_key_from_vault",
            "JWT_SECRET": "mock_jwt_secret_from_vault",
            "ENCRYPTION_KEY": "3pQ-77B69QHIpjN7pZPeUriK25jxbvMBeKkOLlJjtjo=",
            "DATABASE_URL": "sqlite:///./zerodev_from_vault.db",
            "REDIS_HOST": "127.0.0.1",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0",
            "OWNER_EMERGENCY_KEY": "owner_emergency_key_from_vault",
        }

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieves a secret by its name from the mock vault.
        """
        print(f"Fetching secret from mock vault: {secret_name}")
        return self._vault.get(secret_name)


@lru_cache(maxsize=None)
def get_secrets_manager() -> SecretsManager:
    """
    Returns a secrets manager instance based on the environment.
    """
    if settings.ENVIRONMENT == "production":
        vault_addr = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        if not vault_addr or not vault_token:
            raise ValueError(
                "VAULT_ADDR and VAULT_TOKEN must be set in production environment"
            )
        return VaultSecretsManager(vault_addr, vault_token)
    return MockSecretsManager()
