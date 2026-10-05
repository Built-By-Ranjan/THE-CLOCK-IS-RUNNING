from pydantic_settings import BaseSettings, SettingsConfigDict  # Import settings helpers.


class Settings(BaseSettings):  # Define application settings.
    DATABASE_URL: str  # Store the database connection URL.
    GEMINI_API_KEY: str = ""  # Store the optional Gemini API key.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # Load and filter environment values.


settings = Settings()  # Create the shared settings instance.
