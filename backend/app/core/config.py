from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    app_env: str = "development"

    chroma_path: str = "./chroma_data"
    chroma_collection_name: str = "business_documents"
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()