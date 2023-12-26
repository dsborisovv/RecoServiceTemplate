from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)


class LogConfig(Config):
    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="log_")
    level: str = "INFO"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"


class ServiceConfig(Config):
    service_name: str = "reco_service"
    k_recs: int = 10
    valid_token: str = "valid_token"
    list_models: list = ["dummy_model", "tfidf_userknn_popular_model", "lightfm_model", "ranker"]

    log_config: LogConfig


def get_config() -> ServiceConfig:
    return ServiceConfig(
        log_config=LogConfig(),
    )
