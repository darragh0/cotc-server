from pathlib import Path
from typing import Final

from cotc_common.config import BaseConfig, init_base_config
from pydantic import BaseModel

ROOT_PATH: Final[Path] = Path(__file__).parent.parent


class FlaskConfig(BaseModel):
    ENVIRONMENT: str
    SERVER_NAME: str
    DEBUG: bool
    SQLALCHEMY_DATABASE_URI: str


class AppConfig(BaseModel):
    flask: FlaskConfig


class Config(BaseConfig):
    app: AppConfig


def init_config() -> Config:
    base_cfg, app_cfg = init_base_config(ROOT_PATH)

    return Config(
        app=AppConfig(flask=FlaskConfig(**app_cfg["flask"])),
        argparse=base_cfg.argparse,
        argv=base_cfg.argv,
        logging=base_cfg.logging,
    )
