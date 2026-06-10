"""Implements behavior common to all application classes.

Adapted from the IT 566 application framework.
Author:      Leonardo Andres Sandino Acosta
"""

from abc import ABC, abstractmethod
from datasets_and_curators.logging import LoggingService
from datasets_and_curators.settings import Settings


class ApplicationBase(ABC):
    """Abstract base class for all application layer classes.

    Provides shared logging and settings access to all subclasses.
    Subclasses must implement the start() method.
    """

    def __init__(self, subclass_name: str, logfile_prefix_name: str) -> None:
        """Instantiate instance with shared logging and settings."""
        self._settings = Settings().read_settings_file_from_location()
        self._logger = LoggingService(subclass_name, logfile_prefix_name)
