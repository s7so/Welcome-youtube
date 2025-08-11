import logging

logger = logging.getLogger(__name__)


def send_critical(message: str) -> None:
    logger.critical("ALERT: %s", message)