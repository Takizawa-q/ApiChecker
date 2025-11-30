import sys
from pathlib import Path
from typing import Any

from loguru import logger


DEBUG_MODE = False 

class Logger:
    def __init__(self,
                 log_dir: str,
                 compression: str = "gz",
                 serialize: bool = True,
                 backtrace: bool = True,
                 enqueue: bool = True,
                 level: str = "INFO",
                 catch: bool = True) -> None:
        self.enqueue: bool = enqueue
        self.is_debug: bool = DEBUG_MODE
        self.compression: str = compression
        self.serialize: bool = serialize
        self.backtrace: bool = backtrace
        self._catch_enabled: bool = catch  # Переименовано чтобы избежать конфликта
        self.log_dir: str = log_dir
        self.level: str = level
        self.debug_format: str = (
            "{time:YYYY-MM-DD HH:mm:ss:SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{extra} | "
            "{message}"
        )

        self.error_format: str = (
            "<red>{time:YYYY-MM-DD HH:mm:ss:SSS}</red> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "{extra} | "
            "<level>{message}</level>"
        )

        logger.remove()
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)

        self._setup_console_handler()
        self._setup_app_handler(rotation="00:00", retention="30 days")
        if self.is_debug:
            self._setup_debug_handler(rotation="100 MB", retention="3 days")
        self._setup_error_handler(rotation="00:00", retention="90 days")

        self.logger = logger

    def _setup_app_handler(self, rotation: str = "500 MB", retention: str = "7 days") -> None:
        logger.add(
            Path(f"{self.log_dir}/app.log"),
            level="INFO" if not self.is_debug else "DEBUG",
            rotation=rotation,
            retention=retention,
            format=self.debug_format,
            enqueue=self.enqueue,
            serialize=self.serialize,
            compression=self.compression,
            diagnose=self.is_debug,
            backtrace=self.backtrace,
            catch=self._catch_enabled
        )

    def _setup_error_handler(self, rotation: str = "500 MB", retention: str = "7 days") -> None:
        logger.add(
            Path(f"{self.log_dir}/error.log"),
            level="ERROR",
            rotation=rotation,
            retention=retention,
            format=self.error_format,
            enqueue=self.enqueue,
            serialize=self.serialize,
            compression=self.compression,
            diagnose=self.is_debug,
            backtrace=self.backtrace,
            catch=self._catch_enabled
        )

    def _setup_debug_handler(self, rotation: str = "500 MB", retention: str = "7 days") -> None:
        logger.add(
            Path(f"{self.log_dir}/debug.log"),
            level="DEBUG",
            rotation=rotation,
            retention=retention,
            format=self.debug_format,
            enqueue=self.enqueue,
            serialize=self.serialize,
            compression=self.compression,
            diagnose=self.is_debug,
            backtrace=self.backtrace,
            catch=self._catch_enabled
        )

    def _setup_console_handler(self, level: str = "INFO") -> None:
        console_format: str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<yellow>{extra}</yellow> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stderr,
            format=console_format,
            enqueue=self.enqueue,
            level=level if not self.is_debug else "DEBUG",
            backtrace=self.backtrace,
        )

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).warning(message, *args, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).debug(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).critical(message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.opt(depth=1).exception(message, *args, **kwargs)

    def catch(self, *args: Any, **kwargs: Any) -> Any:
        return self.logger.opt(depth=1).catch(*args, **kwargs)

    def bind(self, **kwargs: Any) -> Any:
        """Create a logger with bound context."""
        return self.logger.opt(depth=1).bind(**kwargs)

def get_logger(log_dir="logs", level="INFO") -> Logger:
    return Logger(log_dir=log_dir, level=level)

log = get_logger() 
