# template-ds-repo

This repository provides a template and set of recommended tooling for all Python projects using UV. By following this structure and tooling, you ensure consistency, maintainability, and adherence to best practices across projects.

This repository uses [UV](https://astral.sh/uv) for managing virtual environments and dependencies. UV simplifies venv creation, dependency resolution, installation, and versioning.

## Table of Contents
- [template-ds-repo](#template-ds-repo)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Getting Started](#getting-started)
    - [1. Prerequisites](#1-prerequisites)
        - [MacOS](#macos)
        - [Ubuntu](#ubuntu)
        - [Understanding the Makefiles](#understanding-the-makefiles)
      - [UV installation](#uv-installation)
      - [Docker installation](#docker-installation)
        - [MacOS](#macos-1)
        - [Ubuntu](#ubuntu-1)
    - [2. Configuration (Optional)](#2-configuration-optional)
      - [Choosing a Python version](#choosing-a-python-version)
      - [Configuring the Application Entrypoint](#configuring-the-application-entrypoint)
      - [Other configurations](#other-configurations)
    - [3. Installing Dependencies](#3-installing-dependencies)
    - [4. Managing Dependencies](#4-managing-dependencies)
      - [The Lock File (`uv.lock`)](#the-lock-file-uvlock)
    - [5. Running Code](#5-running-code)
    - [6. Building a Docker Container](#6-building-a-docker-container)
    - [7. Running a Docker Container](#7-running-a-docker-container)
  - [Continuous Integration (CI)](#continuous-integration-ci)
    - [Workflow Overview](#workflow-overview)
    - [The Importance of Tests](#the-importance-of-tests)

## Project Structure

```bash
.
├── .github
│   └── workflows
│       └── run-precommit-and-tests.yaml  # Runs pre-commit hooks and tests
├── .gitignore                    # Files for git to ignore
├── .pre-commit-config.yaml       # Configures pre-commit
├── Makefile                      # Main entry point: Detects OS, includes platform Makefile, runs common tasks.
├── README.md                     # This file!
├── pull_request_template.md      # Template to use for pull requests
├── .env.example                  # Example environment variables file
├── Dockerfile                    # Dockerfile using UV
├── pyproject.toml                # Project configuration (build system / dependencies)
├── uv.lock                       # Exact versions of all dependencies (do not edit manually)
├── src                           # Root of your module - UV will install this automatically
│   └── your_module               # Module name (replace in project.name in pyproject.toml)
│       ├── __init__.py
│       ├── adder.py
│       ├── main.py
│       └── py.typed              # Marker file indicating the package supports type hints 
└── tests
    └── test_example.py
````

## Getting Started

Follow these steps to set up the repository for the first time:

### 1\. Prerequisites

Ensure your machine has a suitable package manager (`brew` or `apt`) and `make` installed.

##### MacOS

First ensure Homebrew is installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then ensure `make` is installed (it often comes with Xcode Command Line Tools, but installing explicitly doesn't hurt):

```bash
brew install make
```

##### Ubuntu

Ensure `apt` is up-to-date:

```bash
sudo apt update
```

Then install `make` and necessary build tools:

```bash
sudo apt install make build-essential
```

##### Understanding the Makefiles

This project uses a Makefile for automation

  * **`Makefile`**: The entry point for all `make` commands (e.g., `make install`). It auto-detects your OS (macOS or Ubuntu/Debian) to install requirements.

#### UV installation
The `Makefile` provides targets to install a specific version of UV onto your system. You will need to restart your shell to invoke `uv` once installed. `Makefile` commands (such as `make install`) will not require you to restart your shell. 

#### Docker installation

Docker desktop is not allowed due to licensing constraints. We therefore use `colima` on MacOS to run the docker daemon. Please follow these instructions to install on MacOS/Ubuntu.

##### MacOS

1.  Ensure `homebrew` is installed
2.  Install Docker, Docker BuildX and Colima
    ```bash
    brew install docker docker-buildx colima
    ```
3.  Link the Docker BuildX plugin to the Docker install
    ```bash
    mkdir -p ~/.docker/cli-plugins  
    ln -sfn $(brew --prefix)/opt/docker-buildx/bin/docker-buildx ~/.docker/cli-plugins/docker-buildx
    ```
4.  Start the colima runtime
    ```bash
    colima start
    ```
5.  Verify installation
    ```bash
    docker buildx version
    ```
    This should output something similar to
    ```bash
    github.com/docker/buildx v0.30.1 Homebrew
    ```

##### Ubuntu

1.  Update APT
    ```bash
    sudo apt update
    ```
2.  Install Docker and Docker BuildX
    ```bash
    sudo apt install -y docker.io docker-buildx
    ```
3.  Start and enable docker
    ```bash
    sudo systemctl start docker
    sudo systemctl enable docker
    ```
4.  Grant your user permissions to use docker without `sudo`
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```
    Note: this should work first time but you may need to restart your ubuntu instance to use docker without `sudo`.
5.  Verify installation
    ```bash
    docker buildx version
    ```
    This should output something similar to
    ```bash
    [github.com/docker/buildx](https://github.com/docker/buildx) 0.21.3 0.21.3-0ubuntu1~24.04.1
    ```

### 2\. Configuration (Optional)

#### Choosing a Python version

The project requires a strict Python version defined in `pyproject.toml` (currently `3.12.10`).

  * **Automatic Management:** When you run `make install` (or `uv sync`), `uv` will automatically download and install the required Python version if it is not present on your system. You do not need to manually install Python using `brew` or `apt` purely for this project.
  * **Changing Versions:** To change the project's Python version, edit the `requires-python` line in `pyproject.toml`.

#### Configuring the Application Entrypoint

The `Makefile` is configured to run a specific module as the main application entry point.

  * **Current Entrypoint:** `your_module.main`
  * **How to Change:** If you rename your source directory or change the main script, update the `APP_ENTRYPOINT` variable in the `Makefile`:
    ```makefile
    # Inside Makefile
    APP_ENTRYPOINT := your_new_module.new_main_script
    ```

#### Other configurations

1.  Copy `.env.example` to `.env`.
2.  Edit the environment variables as desired.
3.  Run your `make` commands normally; they will pick up these values.

You can also override on the command line:

```bash
make install UV_VERSION=0.7.2
```

### 3\. Installing Dependencies

This installs the specified Python version (via the platform Makefile/environment), installs UV, creates a virtual environment, and installs all project and development dependencies:

```bash
make install
```

> *Note:* On Ubuntu this may prompt for your password for `sudo` when installing system packages.

### 4\. Managing Dependencies

This project uses `uv` to manage dependencies, which replaces standard `pip` workflows. Do not use `pip install` manually.

  * **Adding a package:** To add a new library (e.g., pandas) and update `pyproject.toml` and `uv.lock` automatically:
    ```bash
    uv add pandas
    ```
  * **Adding a dev dependency:** To add a tool used only for development (e.g., a new linter):
    ```bash
    uv add --dev some-linter
    ```
  * **Removing a package:**
    ```bash
    uv remove pandas
    ```
  * **Syncing:** If you pull changes from git that include an updated `uv.lock`, run:
    ```bash
    make install
    ```
    (This runs `uv sync` under the hood to ensure your virtual environment matches the lock file).

#### The Lock File (`uv.lock`)

The `uv.lock` file contains the exact versions of every dependency (and transitive dependency) installed in the project.

  * **Do not edit this file manually.**
  * **Always commit this file** to version control. This ensures that every developer and the CI/CD pipeline uses the exact same package versions, preventing "it works on my machine" issues.

### 5\. Running Code

To run your main application (configured in the `run` target, e.g. `src/your_module/main.py`):

```bash
make run
```

This executes `uv run python -m your_module.main`. The `uv run` command ensures the script runs inside the project's isolated virtual environment without requiring you to manually activate it.

### 6\. Building a Docker Container

Build a Docker image using the `Dockerfile` (which uses UV to install dependencies):

```bash
make build-docker
```

The image will be tagged according to `IMAGE_NAME` and `IMAGE_TAG` (override via `.env` or CLI if desired).

**Note on Caching:** The `Dockerfile` is optimized for caching using `uv`. It uses a multi-stage build where dependencies are installed in a separate `builder` stage using `uv` cache mounts. This significantly speeds up repeated builds.

### 7\. Running a Docker Container

Run the built image interactively, injecting your environment variables from `.env`:

```bash
make run-docker
```

-----

## Continuous Integration (CI)

This repository includes a CI setup using GitHub Actions to automatically check code quality and run tests on every push and pull request.

### Workflow Overview

The CI workflow is defined in:

```
.github/workflows/run-precommit-and-tests.yaml
```

On each push or PR, it:

1.  **Checkout Code**
    Retrieves your branch or PR.
2.  **Setup Environment**
    Installs `make` and necessary build tools, then runs `make install`.
3.  **Run Linting**
    Executes `make lint` (via UV run pre-commit) to enforce formatting and static analysis (`black`, `isort`, `ruff`, `mypy`, etc.).
4.  **Run Tests**
    Executes `make test` (via UV run pytest) to discover and run your test suite.

### The Importance of Tests

The `make test` step is only valuable if you write meaningful tests:

  * **Create tests** in `tests/` (or alongside your modules) using `pytest`.
  * If no tests or trivial tests exist, `pytest` may pass with zero tests, giving false confidence.
  * **Aim for high coverage** on your core logic to catch regressions early.

Both `make lint` and `make test` must pass for a “green” CI status. Failing either will block merges until issues are resolved.
