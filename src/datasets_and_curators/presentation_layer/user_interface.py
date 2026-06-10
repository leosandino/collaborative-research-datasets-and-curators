"""Implements the UserInterface — console menu presentation layer.

Handles all user input/output. Routes requests to AppServices.
Applies Ch-13 (Control Flow / menus), Ch-14 (Sequences / list display),
Ch-17/18 (OOP & Inheritance from ApplicationBase).

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

import inspect
from datasets_and_curators.application_base import ApplicationBase
from datasets_and_curators.service_layer.app_services import AppServices

# ---- Console Display Helpers ----

LINE = "=" * 55
DIVIDER = "-" * 55


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{LINE}")
    print(f"  {title}")
    print(LINE)


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"\n[OK] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"\n[ERROR] {message}")


def get_input(prompt: str, optional: bool = False) -> str:
    """Prompt user for input. If optional=True, blank input is allowed."""
    suffix = " (optional, press Enter to skip)" if optional else ""
    return input(f"  {prompt}{suffix}: ").strip()


class UserInterface(ApplicationBase):
    """Console-based user interface for the application.

    Inherits from ApplicationBase for shared logging and settings.
    """

    def __init__(self, config: dict) -> None:
        """Initialize the UserInterface with configuration."""
        self._config_dict = config
        self.META = config["meta"]
        super().__init__(
            subclass_name=self.__class__.__name__,
            logfile_prefix_name=self.META["log_prefix"]
        )
        self._services = AppServices(config)
        self._services.initialize_database()
        self._logger.log_debug(
            f'{inspect.currentframe().f_code.co_name}: UserInterface initialized.'
        )

    def start(self) -> None:
        """Start the main application loop."""
        self._logger.log_info('Application started.')
        self._main_menu()

    # ====================================================================
    # MAIN MENU
    # ====================================================================

    def _main_menu(self) -> None:
        """Display the main menu and route user selections."""
        while True:
            print_header("COLLABORATIVE DATASETS & CURATORS")
            print("  [1] Manage Curators")
            print("  [2] Manage Datasets")
            print("  [3] Assign Curator to Dataset")
            print("  [4] Reports")
            print("  [5] Exit")
            print(LINE)

            choice = input("  Enter choice: ").strip()
            match choice:
                case '1':
                    self._curator_menu()
                case '2':
                    self._dataset_menu()
                case '3':
                    self._assign_menu()
                case '4':
                    self._reports_menu()
                case '5':
                    print("\nGoodbye!\n")
                    self._logger.log_info('Application exited by user.')
                    break
                case _:
                    print_error("Invalid choice. Please enter 1–5.")

    # ====================================================================
    # CURATOR MENUS
    # ====================================================================

    def _curator_menu(self) -> None:
        """Curator management submenu."""
        while True:
            print_header("MANAGE CURATORS")
            print("  [1] Add Curator")
            print("  [2] List All Curators")
            print("  [3] Update Curator")
            print("  [4] Delete Curator")
            print("  [5] View Datasets for a Curator")
            print("  [0] Back to Main Menu")
            print(LINE)

            choice = input("  Enter choice: ").strip()
            match choice:
                case '1':
                    self._add_curator()
                case '2':
                    self._list_curators()
                case '3':
                    self._update_curator()
                case '4':
                    self._delete_curator()
                case '5':
                    self._view_datasets_for_curator()
                case '0':
                    break
                case _:
                    print_error("Invalid choice.")

    def _add_curator(self) -> None:
        """Add a new curator."""
        print_header("ADD CURATOR")
        try:
            name = get_input("Full Name")
            email = get_input("Email Address")
            affiliation = get_input("Affiliation", optional=True)
            curator = self._services.add_curator(name, email, affiliation)
            print_success(f"Curator added — {curator}")
        except Exception as e:
            print_error(str(e))

    def _list_curators(self) -> None:
        """Display all curators."""
        print_header("ALL CURATORS")
        curators = self._services.get_all_curators()
        if not curators:
            print("  No curators found.")
            return
        print(f"  {'ID':<5} {'Name':<25} {'Email':<30} {'Affiliation'}")
        print(DIVIDER)
        for c in curators:
            print(f"  {c.id:<5} {c.name:<25} {c.email:<30} {c.affiliation or ''}")

    def _update_curator(self) -> None:
        """Update an existing curator."""
        print_header("UPDATE CURATOR")
        self._list_curators()
        try:
            curator_id = int(get_input("Enter Curator ID to update"))
            existing = self._services.get_curator_by_id(curator_id)
            if not existing:
                print_error(f"No curator found with ID {curator_id}.")
                return
            print(f"\n  Updating: {existing}")
            name = get_input(f"New Name [{existing.name}]") or existing.name
            email = get_input(f"New Email [{existing.email}]") or existing.email
            affiliation = get_input(f"New Affiliation [{existing.affiliation}]") or existing.affiliation
            curator = self._services.update_curator(curator_id, name, email, affiliation)
            print_success(f"Curator updated — {curator}")
        except ValueError as e:
            print_error(str(e))

    def _delete_curator(self) -> None:
        """Delete a curator."""
        print_header("DELETE CURATOR")
        self._list_curators()
        try:
            curator_id = int(get_input("Enter Curator ID to delete"))
            confirm = input(f"  Confirm delete curator ID {curator_id}? (yes/no): ").strip().lower()
            if confirm == 'yes':
                self._services.delete_curator(curator_id)
                print_success(f"Curator ID {curator_id} deleted.")
            else:
                print("  Delete cancelled.")
        except ValueError as e:
            print_error(str(e))

    def _view_datasets_for_curator(self) -> None:
        """View all datasets assigned to a curator."""
        print_header("DATASETS FOR CURATOR")
        self._list_curators()
        try:
            curator_id = int(get_input("Enter Curator ID"))
            curator = self._services.get_curator_by_id(curator_id)
            if not curator:
                print_error(f"Curator ID {curator_id} not found.")
                return
            print(f"\n  Datasets managed by: {curator.name}")
            print(DIVIDER)
            results = self._services.get_datasets_for_curator(curator_id)
            if not results:
                print("  No datasets found for this curator.")
                return
            for dataset, role, curation_date in results:
                print(f"  Dataset: {dataset.name} | Category: {dataset.category} "
                      f"| Role: {role} | Curation Date: {curation_date}")
        except ValueError as e:
            print_error(str(e))

    # ====================================================================
    # DATASET MENUS
    # ====================================================================

    def _dataset_menu(self) -> None:
        """Dataset management submenu."""
        while True:
            print_header("MANAGE DATASETS")
            print("  [1] Add Dataset")
            print("  [2] List All Datasets")
            print("  [3] Update Dataset")
            print("  [4] Delete Dataset")
            print("  [5] View Curators for a Dataset")
            print("  [0] Back to Main Menu")
            print(LINE)

            choice = input("  Enter choice: ").strip()
            match choice:
                case '1':
                    self._add_dataset()
                case '2':
                    self._list_datasets()
                case '3':
                    self._update_dataset()
                case '4':
                    self._delete_dataset()
                case '5':
                    self._view_curators_for_dataset()
                case '0':
                    break
                case _:
                    print_error("Invalid choice.")

    def _add_dataset(self) -> None:
        """Add a new dataset."""
        print_header("ADD DATASET")
        try:
            name = get_input("Dataset Name")
            description = get_input("Description", optional=True)
            category = get_input("Category (e.g., Climate, Medical, Finance)", optional=True)
            size_gb = get_input("Size in GB (e.g., 1.5)", optional=True) or "0"
            created_date_str = get_input("Created Date (MM/DD/YYYY)", optional=True) or ""
            dataset = self._services.add_dataset(name, description, category, size_gb, created_date_str)
            print_success(f"Dataset added — {dataset}")
        except Exception as e:
            print_error(str(e))

    def _list_datasets(self) -> None:
        """Display all datasets."""
        print_header("ALL DATASETS")
        datasets = self._services.get_all_datasets()
        if not datasets:
            print("  No datasets found.")
            return
        print(f"  {'ID':<5} {'Name':<30} {'Category':<15} {'Size (GB)':<12} {'Created'}")
        print(DIVIDER)
        for d in datasets:
            print(f"  {d.id:<5} {d.name:<30} {d.category or '':<15} "
                  f"{d.size_gb:<12.2f} {d.created_date or ''}")

    def _update_dataset(self) -> None:
        """Update an existing dataset."""
        print_header("UPDATE DATASET")
        self._list_datasets()
        try:
            dataset_id = int(get_input("Enter Dataset ID to update"))
            existing = self._services.get_dataset_by_id(dataset_id)
            if not existing:
                print_error(f"No dataset found with ID {dataset_id}.")
                return
            print(f"\n  Updating: {existing}")
            name = get_input(f"New Name [{existing.name}]") or existing.name
            description = get_input(f"New Description") or existing.description
            category = get_input(f"New Category [{existing.category}]") or existing.category
            size_gb = get_input(f"New Size GB [{existing.size_gb}]") or str(existing.size_gb)
            created_date_str = get_input(f"New Created Date MM/DD/YYYY") or (
                existing.created_date.strftime("%m/%d/%Y") if existing.created_date else "")
            dataset = self._services.update_dataset(
                dataset_id, name, description, category, size_gb, created_date_str)
            print_success(f"Dataset updated — {dataset}")
        except ValueError as e:
            print_error(str(e))

    def _delete_dataset(self) -> None:
        """Delete a dataset."""
        print_header("DELETE DATASET")
        self._list_datasets()
        try:
            dataset_id = int(get_input("Enter Dataset ID to delete"))
            confirm = input(f"  Confirm delete dataset ID {dataset_id}? (yes/no): ").strip().lower()
            if confirm == 'yes':
                self._services.delete_dataset(dataset_id)
                print_success(f"Dataset ID {dataset_id} deleted.")
            else:
                print("  Delete cancelled.")
        except ValueError as e:
            print_error(str(e))

    def _view_curators_for_dataset(self) -> None:
        """View all curators assigned to a dataset."""
        print_header("CURATORS FOR DATASET")
        self._list_datasets()
        try:
            dataset_id = int(get_input("Enter Dataset ID"))
            dataset = self._services.get_dataset_by_id(dataset_id)
            if not dataset:
                print_error(f"Dataset ID {dataset_id} not found.")
                return
            print(f"\n  Curators for dataset: {dataset.name}")
            print(DIVIDER)
            results = self._services.get_curators_for_dataset(dataset_id)
            if not results:
                print("  No curators assigned to this dataset.")
                return
            for curator, role, curation_date in results:
                print(f"  Curator: {curator.name} | Email: {curator.email} "
                      f"| Role: {role} | Curation Date: {curation_date}")
        except ValueError as e:
            print_error(str(e))

    # ====================================================================
    # ASSIGN MENU
    # ====================================================================

    def _assign_menu(self) -> None:
        """Curator-to-Dataset assignment submenu."""
        while True:
            print_header("ASSIGN CURATOR TO DATASET")
            print("  [1] Assign a Curator to a Dataset")
            print("  [2] Remove a Curator from a Dataset")
            print("  [0] Back to Main Menu")
            print(LINE)

            choice = input("  Enter choice: ").strip()
            match choice:
                case '1':
                    self._assign_curator()
                case '2':
                    self._remove_curator()
                case '0':
                    break
                case _:
                    print_error("Invalid choice.")

    def _assign_curator(self) -> None:
        """Assign a curator to a dataset."""
        print_header("ASSIGN CURATOR TO DATASET")
        self._list_datasets()
        try:
            dataset_id = int(get_input("Enter Dataset ID"))
            dataset = self._services.get_dataset_by_id(dataset_id)
            if not dataset:
                print_error(f"Dataset ID {dataset_id} not found.")
                return

            self._list_curators()
            curator_id = int(get_input("Enter Curator ID"))
            curator = self._services.get_curator_by_id(curator_id)
            if not curator:
                print_error(f"Curator ID {curator_id} not found.")
                return

            role = get_input("Role (e.g., Lead, Reviewer, Validator)")
            curation_date_str = get_input("Curation Date MM/DD/YYYY", optional=True) or ""
            self._services.assign_curator_to_dataset(dataset_id, curator_id, role, curation_date_str)
            print_success(f"Curator '{curator.name}' assigned to dataset '{dataset.name}' as '{role}'.")
        except ValueError as e:
            print_error(str(e))
        except Exception as e:
            print_error(f"Assignment failed: {e}")

    def _remove_curator(self) -> None:
        """Remove a curator from a dataset."""
        print_header("REMOVE CURATOR FROM DATASET")
        self._list_datasets()
        try:
            dataset_id = int(get_input("Enter Dataset ID"))
            dataset = self._services.get_dataset_by_id(dataset_id)
            if not dataset:
                print_error(f"Dataset ID {dataset_id} not found.")
                return

            results = self._services.get_curators_for_dataset(dataset_id)
            if not results:
                print("  No curators assigned to this dataset.")
                return

            print(f"\n  Curators for '{dataset.name}':")
            for curator, role, curation_date in results:
                print(f"    ID {curator.id}: {curator.name} | Role: {role}")

            curator_id = int(get_input("Enter Curator ID to remove"))
            self._services.remove_curator_from_dataset(dataset_id, curator_id)
            print_success(f"Curator ID {curator_id} removed from dataset '{dataset.name}'.")
        except ValueError as e:
            print_error(str(e))

    # ====================================================================
    # REPORTS MENU
    # ====================================================================

    def _reports_menu(self) -> None:
        """Reports submenu."""
        while True:
            print_header("REPORTS")
            print("  [1] Full Cross-Reference Report")
            print("  [2] Search Datasets by Category")
            print("  [0] Back to Main Menu")
            print(LINE)

            choice = input("  Enter choice: ").strip()
            match choice:
                case '1':
                    self._full_report()
                case '2':
                    self._search_by_category()
                case '0':
                    break
                case _:
                    print_error("Invalid choice.")

    def _full_report(self) -> None:
        """Display the full curation cross-reference report."""
        print_header("FULL CURATION REPORT")
        rows = self._services.get_full_report()
        if not rows:
            print("  No curation records found.")
            return

        print(f"  {'Dataset':<28} {'Category':<12} {'Curator':<20} {'Role':<12} {'Date'}")
        print(DIVIDER)
        for row in rows:
            print(f"  {row['dataset_name']:<28} {row['category'] or '':<12} "
                  f"{row['curator_name']:<20} {row['role'] or '':<12} {row['curation_date'] or ''}")

    def _search_by_category(self) -> None:
        """Search and display datasets by category."""
        print_header("SEARCH DATASETS BY CATEGORY")
        category = get_input("Enter Category to search")
        datasets = self._services.get_datasets_by_category(category)
        if not datasets:
            print(f"  No datasets found in category '{category}'.")
            return
        print(f"\n  Results for category '{category}':")
        print(DIVIDER)
        print(f"  {'ID':<5} {'Name':<30} {'Size (GB)':<12} {'Created'}")
        for d in datasets:
            print(f"  {d.id:<5} {d.name:<30} {d.size_gb:<12.2f} {d.created_date or ''}")
