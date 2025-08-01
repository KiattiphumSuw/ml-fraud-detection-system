from .secret import SecretSettings
from .settings import BasicSettings, load_basic_settings

_basic = load_basic_settings()
_secrets = SecretSettings()


class Settings:
    """
    Application configuration combining general and sensitive settings.

    Args:
        basic (BasicSettings): General settings loaded from YAML.
        secrets (SecretSettings): Sensitive settings loaded from environment.
    """

    basic: BasicSettings = _basic
    secrets: SecretSettings = _secrets

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct the full database connection URL.

        Returns:
            str: Postgres URL in the form
                 postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
        """
        return (
            f"postgresql://"
            f"{self.secrets.DB_USER}:"
            f"{self.secrets.DB_PASSWORD}@"
            f"{self.basic.DB_HOST}:"
            f"{self.basic.DB_PORT}/"
            f"{self.basic.DB_NAME}"
        )

    @property
    def MODEL_WEIGHT_PATH(self) -> str:
        """
        Path to the serialized model weights file.

        Returns:
            str: File system path where the model is stored.
        """
        return self.basic.MODEL_WEIGHT_PATH

    @property
    def FEATURE_COLS(self) -> list[str]:
        """
        List of feature column names used by the fraud model.

        Returns:
            List[str]: Column names loaded from the YAML config.
        """
        return self.basic.FEATURE_COLS


# singleton instance for import elsewhere
settings = Settings()
