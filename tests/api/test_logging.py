import logging
from pathlib import Path

from app import main
from app.settings import settings


def test_configure_logging_writes_file(tmp_path):
    log_file = Path(tmp_path) / "app-debug.log"
    settings.app_log_path = str(log_file)
    settings.log_level = "DEBUG"

    main.configure_logging()

    test_logger = logging.getLogger("app.test")
    test_logger.debug("debug-log-message")

    for handler in logging.getLogger().handlers:
        if hasattr(handler, "flush"):
            handler.flush()

    assert log_file.exists()
    assert "debug-log-message" in log_file.read_text(encoding="utf-8")
