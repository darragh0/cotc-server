from logging import Logger
from typing import Callable

from cotc_common.util import clear_scr
from flask import Flask

from application.config import Config, init_config
from application.db import DB


class AppBase:
    web_app: Flask
    config: Config
    logger: Logger
    db: DB

    def __init__(self, import_name: str) -> None:
        self.web_app = Flask(import_name)
        self.config = init_config()
        self.logger = self.web_app.logger
        self._init_flask_config()
        self._init_routes()
        self.db = DB(self)

    def run(self, clear: bool = True) -> None:
        if clear:
            clear_scr()
        self.web_app.run()

    def _init_routes(self) -> None:
        for attr in dir(self):
            if attr.startswith("route_"):
                func: Callable = getattr(self, attr)

                if attr.endswith("404"):
                    self.web_app.register_error_handler(404, func)
                    continue

                for route in func.routes:  # type: ignore[attr-defined]
                    self.web_app.route(route, **func.kwargs)(func)  # type: ignore[attr-defined]

    def _init_flask_config(self) -> None:
        self.web_app.config.update(self.config.app.flask.model_dump())
