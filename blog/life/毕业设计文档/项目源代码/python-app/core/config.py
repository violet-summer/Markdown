from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:helloworld@localhost:3306/city"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    assets_base_url: str = "http://localhost:8000/assets"
    assets_storage_dir: str = "./assets"
    api_prefix: str = ""
    app_env: str = "development"
    app_debug: bool = True

    minio_endpoint: str = "127.0.0.1:9000"
    minio_access_key: str = "admin"
    minio_secret_key: str = "helloworld"
    minio_bucket: str = "city"
    minio_region: str | None = None
    minio_secure: bool = False
    minio_root_prefix: str = "app"
    minio_upload_retries: int = 3

    # CORS - local testing override
    cors_allow_all: bool = False
    
    # CORS 配置 - 区分开发和生产环境
    # 开发环境：允许本地所有端口
    # 生产环境：只允许指定的域名
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    
    @property
    def allowed_origins(self) -> List[str]:
        """解析 CORS 允许的源地址列表"""
        if self.cors_allow_all:
            return ["*"]
        if self.app_env == "development":
            # 开发环境：允许所有本地地址
            return [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
            ]
        else:
            # 生产环境：只允许配置的地址
            return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
