from backend.core.settings import settings
from cryptography.fernet import Fernet


class EncryptionService:
    """
    Handles encryption and decryption of data.
    """

    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        """
        Encrypts a string.
        """
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypts a string.
        """
        return self.fernet.decrypt(encrypted_data.encode()).decode()


encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
