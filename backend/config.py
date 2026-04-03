from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ollama_base_url: str = Field(default="https://ollama.com", env="OLLAMA_BASE_URL")
    ollama_api_key: str = Field(default="", env="OLLAMA_API_KEY")
    ollama_model: str = Field(default="llama3.1", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=300, env="OLLAMA_TIMEOUT")
    max_tool_runtime: int = Field(default=300, env="MAX_TOOL_RUNTIME")
    max_tool_output_bytes: int = Field(default=10 * 1024 * 1024, env="MAX_TOOL_OUTPUT_BYTES")  # 10MB
    max_agent_iterations: int = Field(default=15, env="MAX_AGENT_ITERATIONS")
    session_ttl: int = Field(default=3600, env="SESSION_TTL")
    session_db_path: str = Field(default="/data/sessions.db", env="SESSION_DB_PATH")
    loot_dir: str = Field(default="/app/loot", env="LOOT_DIR")

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
