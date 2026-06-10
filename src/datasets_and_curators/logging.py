"""Provides LoggingService convenience class for application logging.

Adapted from the IT 566 application framework.
Author:      Leonardo Andres Sandino Acosta
"""

import logging
import logging.handlers
import os
from datasets_and_curators.settings import Settings


class LoggingService():
    """Provides logging services."""

    def __init__(self, class_name: str, logfile_prefix_name: str = None) -> None:
        """Initialize instance."""
        self._logger = logging.getLogger(class_name)
        self._logger.propagate = False
        self._settings_dict = Settings().read_settings_file_from_location()
        self._logfile_prefix_name = logfile_prefix_name
        self.log_level = logging.ERROR

        match self._settings_dict.get('log_level', 'error'):
            case 'notset':
                self._logger.setLevel(logging.NOTSET)
                self.log_level = logging.NOTSET
            case 'debug':
                self._logger.setLevel(logging.DEBUG)
                self.log_level = logging.DEBUG
            case 'info':
                self._logger.setLevel(logging.INFO)
                self.log_level = logging.INFO
            case 'warning':
                self._logger.setLevel(logging.WARNING)
                self.log_level = logging.WARNING
            case 'error':
                self._logger.setLevel(logging.ERROR)
                self.log_level = logging.ERROR
            case 'critical':
                self._logger.setLevel(logging.CRITICAL)
                self.log_level = logging.CRITICAL
            case _:
                self._logger.setLevel(logging.ERROR)
                self.log_level = logging.ERROR

        self._formatter = logging.Formatter(
            '%(levelname)s:%(name)s:%(asctime)s:%(message)s')

        if not self._logger.handlers:
            if self._settings_dict.get('log_to_console', True):
                ch = logging.StreamHandler()
                ch.setLevel(logging.DEBUG)
                ch.setFormatter(self._formatter)
                self._logger.addHandler(ch)

            if self._settings_dict.get('log_to_file', True):
                logs_dir = self._settings_dict.get('logs_dir', 'logs')
                os.makedirs(logs_dir, exist_ok=True)
                log_file = os.path.join(
                    logs_dir,
                    f"{self._logfile_prefix_name}_{self._settings_dict['log_filename']}")
                fh = logging.handlers.TimedRotatingFileHandler(
                    log_file, when='midnight', backupCount=20)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(self._formatter)
                self._logger.addHandler(fh)

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self._logger.debug(message)

    def log_error(self, message: str) -> None:
        """Log error message."""
        self._logger.error(message)

    def log_info(self, message: str) -> None:
        """Log info message."""
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self._logger.warning(message)

    def log_critical(self, message: str) -> None:
        """Log critical message."""
        self._logger.critical(message)
