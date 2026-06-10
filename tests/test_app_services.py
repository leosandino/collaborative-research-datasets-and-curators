"""Unit tests for domain entity classes and AppServices validation logic.

Tests are designed to run WITHOUT a live database connection, testing
only the domain classes and validation methods.

Applies Ch-25 (Unit Testing) patterns introduced in the course.

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

import sys
import os
import pytest
from datetime import date

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datasets_and_curators.domain.curator import Curator
from datasets_and_curators.domain.dataset import Dataset


# ============================================================
# Curator Entity Tests
# ============================================================

class TestCurator:
    """Tests for the Curator domain entity class."""

    def test_curator_creation_with_all_fields(self):
        """Test that a Curator is created correctly with all fields."""
        curator = Curator(curator_id=1, name="Alice Johnson",
                          email="alice@research.org", affiliation="MIT")
        assert curator.id == 1
        assert curator.name == "Alice Johnson"
        assert curator.email == "alice@research.org"
        assert curator.affiliation == "MIT"

    def test_curator_creation_defaults(self):
        """Test that Curator defaults are empty strings for optional fields."""
        curator = Curator()
        assert curator.id is None
        assert curator.name == ''
        assert curator.email == ''
        assert curator.affiliation == ''

    def test_curator_str_representation(self):
        """Test __str__ returns a readable string."""
        curator = Curator(curator_id=1, name="Bob Smith",
                          email="bob@uni.edu", affiliation="Harvard")
        result = str(curator)
        assert "Bob Smith" in result
        assert "bob@uni.edu" in result

    def test_curator_repr_representation(self):
        """Test __repr__ returns a developer-friendly string."""
        curator = Curator(curator_id=2, name="Carol", email="carol@lab.io", affiliation="")
        result = repr(curator)
        assert "Curator(" in result
        assert "Carol" in result

    def test_curator_equality_by_email(self):
        """Two curators with the same email should be equal."""
        c1 = Curator(curator_id=1, name="Alice", email="same@test.com", affiliation="MIT")
        c2 = Curator(curator_id=99, name="Different Name", email="same@test.com", affiliation="Yale")
        assert c1 == c2

    def test_curator_inequality_different_email(self):
        """Two curators with different emails should not be equal."""
        c1 = Curator(email="alice@test.com")
        c2 = Curator(email="bob@test.com")
        assert c1 != c2

    def test_curator_sorting(self):
        """Test that curators sort alphabetically by name."""
        curators = [
            Curator(name="Zara"),
            Curator(name="Alice"),
            Curator(name="Maria"),
        ]
        sorted_curators = sorted(curators)
        assert sorted_curators[0].name == "Alice"
        assert sorted_curators[1].name == "Maria"
        assert sorted_curators[2].name == "Zara"

    def test_curator_hashable(self):
        """Test that Curator can be stored in a set."""
        c1 = Curator(email="test@test.com")
        c2 = Curator(email="other@test.com")
        curator_set = {c1, c2}
        assert len(curator_set) == 2

    def test_curator_property_setters(self):
        """Test that properties can be updated via setters."""
        curator = Curator()
        curator.name = "New Name"
        curator.email = "new@email.com"
        curator.affiliation = "New University"
        assert curator.name == "New Name"
        assert curator.email == "new@email.com"


# ============================================================
# Dataset Entity Tests
# ============================================================

class TestDataset:
    """Tests for the Dataset domain entity class."""

    def test_dataset_creation_with_all_fields(self):
        """Test that a Dataset is created correctly with all fields."""
        created = date(2023, 1, 15)
        dataset = Dataset(dataset_id=10, name="Climate Data 2023",
                          description="Annual climate measurements",
                          category="Climate", size_gb=5.5,
                          created_date=created)
        assert dataset.id == 10
        assert dataset.name == "Climate Data 2023"
        assert dataset.category == "Climate"
        assert dataset.size_gb == 5.5
        assert dataset.created_date == created

    def test_dataset_creation_defaults(self):
        """Test Dataset defaults."""
        dataset = Dataset()
        assert dataset.id is None
        assert dataset.name == ''
        assert dataset.size_gb == 0.0
        assert dataset.created_date is None

    def test_dataset_str_representation(self):
        """Test __str__ returns a readable string."""
        dataset = Dataset(dataset_id=1, name="Test Dataset", category="Science",
                          size_gb=2.5, created_date=date(2024, 6, 1))
        result = str(dataset)
        assert "Test Dataset" in result
        assert "Science" in result

    def test_dataset_repr_representation(self):
        """Test __repr__ returns a developer-friendly string."""
        dataset = Dataset(dataset_id=5, name="Genome DB")
        result = repr(dataset)
        assert "Dataset(" in result
        assert "Genome DB" in result

    def test_dataset_equality_by_name(self):
        """Two datasets with the same name should be equal."""
        d1 = Dataset(dataset_id=1, name="UniqueDataset", category="Bio")
        d2 = Dataset(dataset_id=99, name="UniqueDataset", category="Other")
        assert d1 == d2

    def test_dataset_inequality_different_names(self):
        """Two datasets with different names should not be equal."""
        d1 = Dataset(name="Alpha Set")
        d2 = Dataset(name="Beta Set")
        assert d1 != d2

    def test_dataset_sorting(self):
        """Test that datasets sort alphabetically by name."""
        datasets = [
            Dataset(name="Zebra Dataset"),
            Dataset(name="Alpha Dataset"),
            Dataset(name="Midpoint Dataset"),
        ]
        sorted_datasets = sorted(datasets)
        assert sorted_datasets[0].name == "Alpha Dataset"
        assert sorted_datasets[-1].name == "Zebra Dataset"

    def test_dataset_hashable(self):
        """Test that Dataset can be stored in a set."""
        d1 = Dataset(name="Set A")
        d2 = Dataset(name="Set B")
        dataset_set = {d1, d2}
        assert len(dataset_set) == 2


# ============================================================
# Validation Logic Tests (testing validate methods directly)
# ============================================================

class TestValidationLogic:
    """Test standalone validation logic that mirrors what AppServices checks."""

    def test_valid_email_formats(self):
        """Test common valid email formats pass."""
        import re
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        valid_emails = [
            "user@example.com",
            "leo.sandino@marymount.edu",
            "test+filter@domain.org",
        ]
        for email in valid_emails:
            assert re.match(pattern, email), f"{email} should be valid"

    def test_invalid_email_formats(self):
        """Test invalid email formats fail."""
        import re
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        invalid_emails = [
            "notanemail",
            "@nodomain.com",
            "missing-at-sign.com",
            "",
        ]
        for email in invalid_emails:
            assert not re.match(pattern, email), f"{email} should be invalid"

    def test_valid_date_parsing(self):
        """Test that MM/DD/YYYY dates parse correctly."""
        from datetime import datetime
        date_str = "06/10/2026"
        parsed = datetime.strptime(date_str, "%m/%d/%Y").date()
        assert parsed == date(2026, 6, 10)

    def test_invalid_date_raises_error(self):
        """Test that invalid date strings raise ValueError."""
        from datetime import datetime
        with pytest.raises(ValueError):
            datetime.strptime("not-a-date", "%m/%d/%Y")

    def test_positive_float_parsing(self):
        """Test that positive floats parse correctly."""
        value = float("3.14")
        assert value == 3.14
        assert value >= 0

    def test_negative_float_rejected(self):
        """Test that negative values are detected."""
        value = float("-1.5")
        assert value < 0  # caller should reject this
