from pathlib import Path
from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()
    
    
class AuthJWT(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    token_expire_minutes: int = 60
    token_expire_days: int = 30


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    
    naming_convention: dict[str,str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    

class FilesConfig(BaseModel):
    base_dir: Path = BASE_DIR
    static_files: str = "static"
    image_files: str = "static/landing/uploads/images"
    landing_templates: str = "templates/landing"
    admin_templates: str = "templates/admin"
    allowed_image_types: list[str] = ["image_desktop", "image_mobile"]
    allowed_image_formats: list[str] = ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]
    alloewd_image_actions: list[str] = ["image_delete", "image_refresh"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / "env" / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="allow",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    auth: AuthJWT = AuthJWT()
    files: FilesConfig = FilesConfig()
    db: DatabaseConfig


settings = Settings()