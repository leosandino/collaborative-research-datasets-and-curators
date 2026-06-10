"""Defines the MySQLPersistenceWrapper class.

Handles all database operations for the Collaborative Research
Datasets and Curators application. Applies Ch-23 (Relational Database
Fundamentals) and Ch-24 (Scripting The Database).

Author:      Leonardo Andres Sandino Acosta
Project:     IT 566 Final Project
"""

import inspect
import json
from datetime import date

from mysql import connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool

from datasets_and_curators.application_base import ApplicationBase
from datasets_and_curators.domain.curator import Curator
from datasets_and_curators.domain.dataset import Dataset


# ---- SQL String Constants ----

SQL_CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS {db_name};"

SQL_USE_DATABASE = "USE {db_name};"

SQL_CREATE_TABLE_CURATOR = """
CREATE TABLE IF NOT EXISTS curator (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    affiliation VARCHAR(150)
);
"""

SQL_CREATE_TABLE_DATASET = """
CREATE TABLE IF NOT EXISTS dataset (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) UNIQUE NOT NULL,
    description  TEXT,
    category     VARCHAR(50),
    size_gb      DECIMAL(10, 2),
    created_date DATE
);
"""

SQL_CREATE_TABLE_XREF = """
CREATE TABLE IF NOT EXISTS dataset_curation_xref (
    dataset_id    INT NOT NULL,
    curator_id    INT NOT NULL,
    role          VARCHAR(50),
    curation_date DATE,
    PRIMARY KEY (dataset_id, curator_id),
    FOREIGN KEY (dataset_id) REFERENCES dataset(id) ON DELETE CASCADE,
    FOREIGN KEY (curator_id) REFERENCES curator(id) ON DELETE CASCADE
);
"""

# Curator CRUD
SQL_INSERT_CURATOR = "INSERT INTO curator (name, email, affiliation) VALUES (%s, %s, %s);"
SQL_SELECT_ALL_CURATORS = "SELECT id, name, email, affiliation FROM curator ORDER BY name;"
SQL_SELECT_CURATOR_BY_ID = "SELECT id, name, email, affiliation FROM curator WHERE id = %s;"
SQL_SELECT_CURATOR_BY_EMAIL = "SELECT id, name, email, affiliation FROM curator WHERE email = %s;"
SQL_UPDATE_CURATOR = "UPDATE curator SET name=%s, email=%s, affiliation=%s WHERE id=%s;"
SQL_DELETE_CURATOR = "DELETE FROM curator WHERE id=%s;"

# Dataset CRUD
SQL_INSERT_DATASET = "INSERT INTO dataset (name, description, category, size_gb, created_date) VALUES (%s, %s, %s, %s, %s);"
SQL_SELECT_ALL_DATASETS = "SELECT id, name, description, category, size_gb, created_date FROM dataset ORDER BY name;"
SQL_SELECT_DATASET_BY_ID = "SELECT id, name, description, category, size_gb, created_date FROM dataset WHERE id = %s;"
SQL_SELECT_DATASETS_BY_CATEGORY = "SELECT id, name, description, category, size_gb, created_date FROM dataset WHERE category = %s ORDER BY name;"
SQL_UPDATE_DATASET = "UPDATE dataset SET name=%s, description=%s, category=%s, size_gb=%s, created_date=%s WHERE id=%s;"
SQL_DELETE_DATASET = "DELETE FROM dataset WHERE id=%s;"

# Cross-Reference CRUD
SQL_INSERT_XREF = "INSERT INTO dataset_curation_xref (dataset_id, curator_id, role, curation_date) VALUES (%s, %s, %s, %s);"
SQL_DELETE_XREF = "DELETE FROM dataset_curation_xref WHERE dataset_id=%s AND curator_id=%s;"
SQL_SELECT_CURATORS_FOR_DATASET = """
    SELECT c.id, c.name, c.email, c.affiliation, x.role, x.curation_date
    FROM curator c
    JOIN dataset_curation_xref x ON c.id = x.curator_id
    WHERE x.dataset_id = %s
    ORDER BY c.name;
"""
SQL_SELECT_DATASETS_FOR_CURATOR = """
    SELECT d.id, d.name, d.description, d.category, d.size_gb, d.created_date, x.role, x.curation_date
    FROM dataset d
    JOIN dataset_curation_xref x ON d.id = x.dataset_id
    WHERE x.curator_id = %s
    ORDER BY d.name;
"""
SQL_SELECT_FULL_REPORT = """
    SELECT d.name AS dataset_name, d.category, c.name AS curator_name,
           c.email, x.role, x.curation_date
    FROM dataset d
    JOIN dataset_curation_xref x ON d.id = x.dataset_id
    JOIN curator c ON c.id = x.curator_id
    ORDER BY d.name, c.name;
"""


class MySQLPersistenceWrapper(ApplicationBase):
    """Handles all MySQL database operations for the application.

    Inherits from ApplicationBase to access shared logging and settings.
    """

    def __init__(self, config: dict) -> None:
        """Initialize the persistence wrapper with database configuration."""
        self._config_dict = config
        self.META = config["meta"]
        self.DATABASE = config["database"]

        super().__init__(
            subclass_name=self.__class__.__name__,
            logfile_prefix_name=self.META["log_prefix"]
        )
        self._logger.log_debug(
            f'{inspect.currentframe().f_code.co_name}: MySQLPersistenceWrapper initialized.'
        )

        # Build connection config dict
        self.DB_CONFIG = {
            'database': self.DATABASE["connection"]["config"]["database"],
            'user':     self.DATABASE["connection"]["config"]["user"],
            'password': self.DATABASE["connection"]["config"]["password"],
            'host':     self.DATABASE["connection"]["config"]["host"],
            'port':     self.DATABASE["connection"]["config"]["port"],
        }

        self._connection_pool = None

    # ---- Database Initialization ----

    def initialize_database(self) -> None:
        """Create the database and all tables if they do not exist."""
        db_name = self.DATABASE["name"]
        self._logger.log_info(f'Initializing database: {db_name}')

        # Connect without specifying a database to create it
        try:
            cnx = connector.connect(
                user=self.DB_CONFIG['user'],
                password=self.DB_CONFIG['password'],
                host=self.DB_CONFIG['host'],
                port=self.DB_CONFIG['port'],
                use_pure=self.DATABASE["pool"]["use_pure"]
            )
            cursor = cnx.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
            cursor.execute(f"USE `{db_name}`;")
            cursor.execute(SQL_CREATE_TABLE_CURATOR)
            cursor.execute(SQL_CREATE_TABLE_DATASET)
            cursor.execute(SQL_CREATE_TABLE_XREF)
            cnx.commit()
            cursor.close()
            cnx.close()
            self._logger.log_info('Database and tables created successfully.')
            print(f"[OK] Database '{db_name}' and all tables created/verified.")
        except MySQLError as err:
            self._logger.log_error(f'Database initialization error: {err}')
            raise

        # Now initialize connection pool
        self._connection_pool = self._initialize_database_connection_pool(self.DB_CONFIG)

    def _initialize_database_connection_pool(self, config: dict) -> MySQLConnectionPool:
        """Initialize MySQL connection pool."""
        try:
            cnx_pool = MySQLConnectionPool(
                pool_name=self.DATABASE["pool"]["name"],
                pool_size=self.DATABASE["pool"]["size"],
                pool_reset_session=self.DATABASE["pool"]["reset_session"],
                use_pure=self.DATABASE["pool"]["use_pure"],
                **config
            )
            self._logger.log_debug('Connection pool created successfully.')
            return cnx_pool
        except MySQLError as err:
            self._logger.log_error(f'Connection pool creation failed: {err}')
            raise

    def _get_connection(self):
        """Get a connection from the pool."""
        if self._connection_pool is None:
            self._connection_pool = self._initialize_database_connection_pool(self.DB_CONFIG)
        return self._connection_pool.get_connection()

    # ---- Curator CRUD ----

    def add_curator(self, curator: Curator) -> int:
        """Insert a new curator into the database. Returns the new ID."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_INSERT_CURATOR, (curator.name, curator.email, curator.affiliation))
            cnx.commit()
            new_id = cursor.lastrowid
            self._logger.log_info(f'Added curator: {curator.name} (id={new_id})')
            return new_id
        except MySQLError as err:
            self._logger.log_error(f'add_curator error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_all_curators(self) -> list:
        """Return list of all Curator objects."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_ALL_CURATORS)
            rows = cursor.fetchall()
            return [Curator(curator_id=r[0], name=r[1], email=r[2], affiliation=r[3]) for r in rows]
        except MySQLError as err:
            self._logger.log_error(f'get_all_curators error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_curator_by_id(self, curator_id: int) -> Curator:
        """Return a Curator by ID, or None if not found."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_CURATOR_BY_ID, (curator_id,))
            row = cursor.fetchone()
            if row:
                return Curator(curator_id=row[0], name=row[1], email=row[2], affiliation=row[3])
            return None
        except MySQLError as err:
            self._logger.log_error(f'get_curator_by_id error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def update_curator(self, curator: Curator) -> None:
        """Update an existing curator record."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_UPDATE_CURATOR, (curator.name, curator.email, curator.affiliation, curator.id))
            cnx.commit()
            self._logger.log_info(f'Updated curator id={curator.id}')
        except MySQLError as err:
            self._logger.log_error(f'update_curator error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def delete_curator(self, curator_id: int) -> None:
        """Delete a curator by ID."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_DELETE_CURATOR, (curator_id,))
            cnx.commit()
            self._logger.log_info(f'Deleted curator id={curator_id}')
        except MySQLError as err:
            self._logger.log_error(f'delete_curator error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    # ---- Dataset CRUD ----

    def add_dataset(self, dataset: Dataset) -> int:
        """Insert a new dataset into the database. Returns the new ID."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_INSERT_DATASET, (
                dataset.name, dataset.description, dataset.category,
                dataset.size_gb, dataset.created_date
            ))
            cnx.commit()
            new_id = cursor.lastrowid
            self._logger.log_info(f'Added dataset: {dataset.name} (id={new_id})')
            return new_id
        except MySQLError as err:
            self._logger.log_error(f'add_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_all_datasets(self) -> list:
        """Return list of all Dataset objects."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_ALL_DATASETS)
            rows = cursor.fetchall()
            return [Dataset(dataset_id=r[0], name=r[1], description=r[2],
                            category=r[3], size_gb=float(r[4] or 0),
                            created_date=r[5]) for r in rows]
        except MySQLError as err:
            self._logger.log_error(f'get_all_datasets error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        """Return a Dataset by ID, or None if not found."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_DATASET_BY_ID, (dataset_id,))
            row = cursor.fetchone()
            if row:
                return Dataset(dataset_id=row[0], name=row[1], description=row[2],
                               category=row[3], size_gb=float(row[4] or 0), created_date=row[5])
            return None
        except MySQLError as err:
            self._logger.log_error(f'get_dataset_by_id error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_datasets_by_category(self, category: str) -> list:
        """Return list of Datasets matching a category."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_DATASETS_BY_CATEGORY, (category,))
            rows = cursor.fetchall()
            return [Dataset(dataset_id=r[0], name=r[1], description=r[2],
                            category=r[3], size_gb=float(r[4] or 0), created_date=r[5]) for r in rows]
        except MySQLError as err:
            self._logger.log_error(f'get_datasets_by_category error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def update_dataset(self, dataset: Dataset) -> None:
        """Update an existing dataset record."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_UPDATE_DATASET, (
                dataset.name, dataset.description, dataset.category,
                dataset.size_gb, dataset.created_date, dataset.id
            ))
            cnx.commit()
            self._logger.log_info(f'Updated dataset id={dataset.id}')
        except MySQLError as err:
            self._logger.log_error(f'update_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def delete_dataset(self, dataset_id: int) -> None:
        """Delete a dataset by ID."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_DELETE_DATASET, (dataset_id,))
            cnx.commit()
            self._logger.log_info(f'Deleted dataset id={dataset_id}')
        except MySQLError as err:
            self._logger.log_error(f'delete_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    # ---- Cross-Reference Operations ----

    def assign_curator_to_dataset(self, dataset_id: int, curator_id: int,
                                   role: str, curation_date: date) -> None:
        """Assign a curator to a dataset with a role and date."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_INSERT_XREF, (dataset_id, curator_id, role, curation_date))
            cnx.commit()
            self._logger.log_info(
                f'Assigned curator id={curator_id} to dataset id={dataset_id} as {role}')
        except MySQLError as err:
            self._logger.log_error(f'assign_curator_to_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def remove_curator_from_dataset(self, dataset_id: int, curator_id: int) -> None:
        """Remove a curator assignment from a dataset."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_DELETE_XREF, (dataset_id, curator_id))
            cnx.commit()
            self._logger.log_info(
                f'Removed curator id={curator_id} from dataset id={dataset_id}')
        except MySQLError as err:
            self._logger.log_error(f'remove_curator_from_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_curators_for_dataset(self, dataset_id: int) -> list:
        """Return list of (Curator, role, curation_date) tuples for a dataset."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_CURATORS_FOR_DATASET, (dataset_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                curator = Curator(curator_id=r[0], name=r[1], email=r[2], affiliation=r[3])
                result.append((curator, r[4], r[5]))  # (Curator, role, curation_date)
            return result
        except MySQLError as err:
            self._logger.log_error(f'get_curators_for_dataset error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_datasets_for_curator(self, curator_id: int) -> list:
        """Return list of (Dataset, role, curation_date) tuples for a curator."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_DATASETS_FOR_CURATOR, (curator_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                dataset = Dataset(dataset_id=r[0], name=r[1], description=r[2],
                                  category=r[3], size_gb=float(r[4] or 0), created_date=r[5])
                result.append((dataset, r[6], r[7]))  # (Dataset, role, curation_date)
            return result
        except MySQLError as err:
            self._logger.log_error(f'get_datasets_for_curator error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()

    def get_full_report(self) -> list:
        """Return the full cross-reference report as a list of dicts."""
        cnx = self._get_connection()
        try:
            cursor = cnx.cursor()
            cursor.execute(SQL_SELECT_FULL_REPORT)
            rows = cursor.fetchall()
            return [
                {
                    'dataset_name': r[0],
                    'category': r[1],
                    'curator_name': r[2],
                    'email': r[3],
                    'role': r[4],
                    'curation_date': r[5]
                }
                for r in rows
            ]
        except MySQLError as err:
            self._logger.log_error(f'get_full_report error: {err}')
            raise
        finally:
            cursor.close()
            cnx.close()
