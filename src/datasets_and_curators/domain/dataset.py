"""Defines the Dataset domain entity class.

Applies Ch-17 (Classes & OOP), Ch-19 (Well-Behaved Objects).

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

from datetime import date


class Dataset:
    """Represents a research dataset managed by one or more curators.

    A dataset has a name, description, category, size in GB, and a
    creation date. Multiple curators can be assigned to a dataset,
    and a curator can manage multiple datasets (many-to-many relationship).
    """

    def __init__(self,
                 dataset_id: int = None,
                 name: str = '',
                 description: str = '',
                 category: str = '',
                 size_gb: float = 0.0,
                 created_date: date = None) -> None:
        """Initialize a Dataset instance.

        Args:
            dataset_id (int): Database primary key (None for new records).
            name (str): Unique dataset name.
            description (str): Brief description of the dataset.
            category (str): Research category or domain.
            size_gb (float): Dataset size in gigabytes.
            created_date (date): Date the dataset was originally created.
        """
        self._id = dataset_id
        self._name = name
        self._description = description
        self._category = category
        self._size_gb = size_gb
        self._created_date = created_date

    # ---- Properties ----

    @property
    def id(self) -> int:
        """Return dataset database ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def name(self) -> str:
        """Return dataset name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def description(self) -> str:
        """Return dataset description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    def category(self) -> str:
        """Return dataset category."""
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        self._category = value

    @property
    def size_gb(self) -> float:
        """Return dataset size in GB."""
        return self._size_gb

    @size_gb.setter
    def size_gb(self, value: float) -> None:
        self._size_gb = value

    @property
    def created_date(self) -> date:
        """Return dataset creation date."""
        return self._created_date

    @created_date.setter
    def created_date(self, value: date) -> None:
        self._created_date = value

    # ---- Well-Behaved Object Methods (Ch-19) ----

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return (f"Dataset(id={self._id}, name='{self._name}', "
                f"category='{self._category}', size_gb={self._size_gb}, "
                f"created={self._created_date})")

    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        return (f"Dataset(dataset_id={self._id!r}, name={self._name!r}, "
                f"description={self._description!r}, category={self._category!r}, "
                f"size_gb={self._size_gb!r}, created_date={self._created_date!r})")

    def __eq__(self, other: object) -> bool:
        """Compare datasets by name (unique identifier)."""
        if not isinstance(other, Dataset):
            return NotImplemented
        return self._name == other._name

    def __lt__(self, other: 'Dataset') -> bool:
        """Support sorting by name."""
        if not isinstance(other, Dataset):
            return NotImplemented
        return self._name.lower() < other._name.lower()

    def __hash__(self) -> int:
        """Support use in sets and dict keys."""
        return hash(self._name)
