"""Defines the Curator domain entity class.

Applies Ch-17 (Classes & OOP), Ch-19 (Well-Behaved Objects).

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

from datetime import date


class Curator:
    """Represents a curator who manages research datasets.

    A curator has a name, email address, and institutional affiliation.
    Multiple curators can manage the same dataset, and a single curator
    can manage multiple datasets (many-to-many via dataset_curation_xref).
    """

    def __init__(self,
                 curator_id: int = None,
                 name: str = '',
                 email: str = '',
                 affiliation: str = '') -> None:
        """Initialize a Curator instance.

        Args:
            curator_id (int): Database primary key (None for new records).
            name (str): Full name of the curator.
            email (str): Email address (must be unique).
            affiliation (str): Institutional or organizational affiliation.
        """
        self._id = curator_id
        self._name = name
        self._email = email
        self._affiliation = affiliation

    # ---- Properties ----

    @property
    def id(self) -> int:
        """Return curator database ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def name(self) -> str:
        """Return curator name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def email(self) -> str:
        """Return curator email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def affiliation(self) -> str:
        """Return curator affiliation."""
        return self._affiliation

    @affiliation.setter
    def affiliation(self, value: str) -> None:
        self._affiliation = value

    # ---- Well-Behaved Object Methods (Ch-19) ----

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return (f"Curator(id={self._id}, name='{self._name}', "
                f"email='{self._email}', affiliation='{self._affiliation}')")

    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        return (f"Curator(curator_id={self._id!r}, name={self._name!r}, "
                f"email={self._email!r}, affiliation={self._affiliation!r})")

    def __eq__(self, other: object) -> bool:
        """Compare curators by email (unique identifier)."""
        if not isinstance(other, Curator):
            return NotImplemented
        return self._email == other._email

    def __lt__(self, other: 'Curator') -> bool:
        """Support sorting by name."""
        if not isinstance(other, Curator):
            return NotImplemented
        return self._name.lower() < other._name.lower()

    def __hash__(self) -> int:
        """Support use in sets and dict keys."""
        return hash(self._email)
