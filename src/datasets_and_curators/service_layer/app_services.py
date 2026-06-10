"""Implements AppServices — the business logic layer.

Bridges the presentation layer and the persistence layer.
Applies validation rules and coordinates database operations.

Applies Ch-12 (Modules & Functions), Ch-17/18 (OOP & Inheritance).

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

import inspect
import re
from datetime import date, datetime

from datasets_and_curators.application_base import ApplicationBase
from datasets_and_curators.domain.curator import Curator
from datasets_and_curators.domain.dataset import Dataset
from datasets_and_curators.persistence_layer.mysql_persistence_wrapper import MySQLPersistenceWrapper


class AppServices(ApplicationBase):
    """Business logic and validation layer.

    Validates user input and routes operations to the persistence layer.
    Inherits from ApplicationBase for logging and settings access.
    """

    def __init__(self, config: dict) -> None:
        """Initialize AppServices with the application configuration."""
        self._config_dict = config
        self.META = config["meta"]
        super().__init__(
            subclass_name=self.__class__.__name__,
            logfile_prefix_name=self.META["log_prefix"]
        )
        self.DB = MySQLPersistenceWrapper(config)
        self._logger.log_debug(
            f'{inspect.currentframe().f_code.co_name}: AppServices initialized.'
        )

    # ---- Validation Utilities ----

    def validate_email(self, email: str) -> bool:
        """Return True if email is a valid format."""
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    def validate_date_string(self, date_str: str) -> date:
        """Parse and validate a date string in MM/DD/YYYY format.

        Returns:
            date: Parsed date object.

        Raises:
            ValueError: If the format or values are invalid.
        """
        date_str = date_str.strip()
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            raise ValueError(f"Invalid date '{date_str}'. Use MM/DD/YYYY format (e.g., 06/10/2026).")

    def validate_not_empty(self, value: str, field_name: str) -> str:
        """Return stripped value or raise ValueError if empty."""
        value = value.strip()
        if not value:
            raise ValueError(f"'{field_name}' cannot be empty.")
        return value

    def validate_positive_float(self, value: str, field_name: str) -> float:
        """Parse a float from string, raising ValueError if invalid or negative."""
        try:
            f = float(value)
            if f < 0:
                raise ValueError
            return f
        except ValueError:
            raise ValueError(f"'{field_name}' must be a non-negative number.")

    # ---- Curator Service Methods ----

    def add_curator(self, name: str, email: str, affiliation: str) -> Curator:
        """Validate and add a new curator.

        Returns:
            Curator: The newly created curator with its database ID.

        Raises:
            ValueError: If any field fails validation.
        """
        name = self.validate_not_empty(name, "Name")
        email = self.validate_not_empty(email, "Email")
        if not self.validate_email(email):
            raise ValueError(f"'{email}' is not a valid email address.")

        curator = Curator(name=name, email=email, affiliation=affiliation.strip())
        new_id = self.DB.add_curator(curator)
        curator.id = new_id
        self._logger.log_info(f'AppServices: Curator added — {curator}')
        return curator

    def get_all_curators(self) -> list:
        """Return all curators sorted by name."""
        return sorted(self.DB.get_all_curators())

    def get_curator_by_id(self, curator_id: int) -> Curator:
        """Return a curator by ID, or None."""
        return self.DB.get_curator_by_id(curator_id)

    def update_curator(self, curator_id: int, name: str, email: str, affiliation: str) -> Curator:
        """Validate and update an existing curator."""
        name = self.validate_not_empty(name, "Name")
        email = self.validate_not_empty(email, "Email")
        if not self.validate_email(email):
            raise ValueError(f"'{email}' is not a valid email address.")

        curator = Curator(curator_id=curator_id, name=name, email=email, affiliation=affiliation.strip())
        self.DB.update_curator(curator)
        self._logger.log_info(f'AppServices: Curator updated — {curator}')
        return curator

    def delete_curator(self, curator_id: int) -> None:
        """Delete a curator by ID."""
        self.DB.delete_curator(curator_id)
        self._logger.log_info(f'AppServices: Curator id={curator_id} deleted.')

    # ---- Dataset Service Methods ----

    def add_dataset(self, name: str, description: str, category: str,
                    size_gb: str, created_date_str: str) -> Dataset:
        """Validate and add a new dataset.

        Returns:
            Dataset: The newly created dataset with its database ID.
        """
        name = self.validate_not_empty(name, "Name")
        size_gb = self.validate_positive_float(size_gb, "Size (GB)")
        created_date = self.validate_date_string(created_date_str) if created_date_str.strip() else None

        dataset = Dataset(name=name, description=description.strip(),
                          category=category.strip(), size_gb=size_gb,
                          created_date=created_date)
        new_id = self.DB.add_dataset(dataset)
        dataset.id = new_id
        self._logger.log_info(f'AppServices: Dataset added — {dataset}')
        return dataset

    def get_all_datasets(self) -> list:
        """Return all datasets sorted by name."""
        return sorted(self.DB.get_all_datasets())

    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        """Return a dataset by ID, or None."""
        return self.DB.get_dataset_by_id(dataset_id)

    def get_datasets_by_category(self, category: str) -> list:
        """Return datasets matching a category."""
        return self.DB.get_datasets_by_category(category.strip())

    def update_dataset(self, dataset_id: int, name: str, description: str,
                       category: str, size_gb: str, created_date_str: str) -> Dataset:
        """Validate and update an existing dataset."""
        name = self.validate_not_empty(name, "Name")
        size_gb = self.validate_positive_float(size_gb, "Size (GB)")
        created_date = self.validate_date_string(created_date_str) if created_date_str.strip() else None

        dataset = Dataset(dataset_id=dataset_id, name=name, description=description.strip(),
                          category=category.strip(), size_gb=size_gb, created_date=created_date)
        self.DB.update_dataset(dataset)
        self._logger.log_info(f'AppServices: Dataset updated — {dataset}')
        return dataset

    def delete_dataset(self, dataset_id: int) -> None:
        """Delete a dataset by ID."""
        self.DB.delete_dataset(dataset_id)
        self._logger.log_info(f'AppServices: Dataset id={dataset_id} deleted.')

    # ---- Cross-Reference Service Methods ----

    def assign_curator_to_dataset(self, dataset_id: int, curator_id: int,
                                   role: str, curation_date_str: str) -> None:
        """Validate and assign a curator to a dataset."""
        role = self.validate_not_empty(role, "Role")
        curation_date = self.validate_date_string(curation_date_str) if curation_date_str.strip() else date.today()
        self.DB.assign_curator_to_dataset(dataset_id, curator_id, role, curation_date)

    def remove_curator_from_dataset(self, dataset_id: int, curator_id: int) -> None:
        """Remove a curator assignment from a dataset."""
        self.DB.remove_curator_from_dataset(dataset_id, curator_id)

    def get_curators_for_dataset(self, dataset_id: int) -> list:
        """Return list of (Curator, role, curation_date) for a dataset."""
        return self.DB.get_curators_for_dataset(dataset_id)

    def get_datasets_for_curator(self, curator_id: int) -> list:
        """Return list of (Dataset, role, curation_date) for a curator."""
        return self.DB.get_datasets_for_curator(curator_id)

    def get_full_report(self) -> list:
        """Return the full cross-reference curation report."""
        return self.DB.get_full_report()

    # ---- Database Initialization ----

    def initialize_database(self) -> None:
        """Initialize database and create tables."""
        self.DB.initialize_database()
