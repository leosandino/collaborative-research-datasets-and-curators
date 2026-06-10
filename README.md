# Collaborative Research Datasets and Curators

**IT 566: Computer Scripting Techniques — Summer 2026 Final Project**  
**Student:** Leonardo Andres Sandino Acosta  
**Due Date:** Saturday, August 01, 2026

---

## Project Description

A console-based, multi-layered, data-driven application that manages collaborative research datasets and the curators who maintain them.

**Primary Entities:**
- **Dataset** — A research dataset with name, description, category, size, and creation date.
- **Curator** — A person who manages datasets, with name, email, and institutional affiliation.

**Relationship:** A curator can manage many datasets; a dataset can have many curators. The cross-reference table `dataset_curation_xref` captures each curator's **role** and **curation date** per dataset.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Application language |
| MySQL | Relational database backend |
| mysql-connector-python | Python-MySQL interface |
| Pipenv | Virtual environment & dependency management |
| pytest | Unit testing |
| Bash | Build automation (build.sh) |
| Git / GitHub | Source control with regular commits |

---

## Project Structure

```
collaborative-research-datasets-and-curators/
├── .gitignore
├── README.md
├── Pipfile                          # Pipenv dependencies
├── build.sh                         # Bash build/test/run script
├── config/
│   └── datasets_curators_config.json  # DB connection config
├── logs/                            # Log output (gitignored)
├── src/
│   ├── main.py                      # Application entry point
│   └── datasets_and_curators/       # Application package
│       ├── application_base.py      # Abstract base class
│       ├── logging.py               # LoggingService
│       ├── settings.py              # Settings management
│       ├── domain/
│       │   ├── dataset.py           # Dataset entity class
│       │   └── curator.py           # Curator entity class
│       ├── persistence_layer/
│       │   └── mysql_persistence_wrapper.py  # MySQL CRUD operations
│       ├── service_layer/
│       │   └── app_services.py      # Business logic
│       └── presentation_layer/
│           └── user_interface.py    # Console menu interface
└── tests/
    └── test_app_services.py         # Unit tests
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- MySQL Server (Community Edition)
- Pipenv (`pip install pipenv`)

### 1. Install Dependencies
```bash
pipenv --python 3.12
pipenv install
```

### 2. Configure the Database
Edit `config/datasets_curators_config.json` with your MySQL credentials.

### 3. Initialize the Database
```bash
bash build.sh init
```

### 4. Run the Application
```bash
bash build.sh run
```

### 5. Run Tests
```bash
bash build.sh test
```

---

## Application Menu

```
====================================
  COLLABORATIVE DATASETS & CURATORS
====================================
[1] Manage Curators
[2] Manage Datasets
[3] Assign Curator to Dataset
[4] Reports
[5] Exit
====================================
```

---

## Course Book Alignment

This project applies material from **Chapters 1–24** of *Computer Scripting Techniques with Python*:

- **Ch-08:** Git/GitHub — regular commits throughout development
- **Ch-09:** Project organization with layered src structure
- **Ch-10:** Pipenv virtual environment management
- **Ch-11:** Bash build automation script
- **Ch-12–15:** Modules, control flow, sequences, dictionaries
- **Ch-16:** File I/O — reading JSON config and writing logs
- **Ch-17–19:** OOP — classes, inheritance from ApplicationBase, well-behaved objects
- **Ch-20–21:** Networking / client-server model (MySQL is a server)
- **Ch-23–24:** Relational database fundamentals and scripting with Python

---

## Commit Log

| Date | Milestone |
|------|-----------|
| 2026-06-10 | Initial project scaffold — framework adapted, structure created |
