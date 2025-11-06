# Gemini Project Context: Compass Automation

## Project Overview

This project is a Python-based automation framework for the **Compass Mobile PWA**. It uses **Selenium WebDriver** with **Microsoft Edge** to automate and test workflows related to Preventive Maintenance (PM) for fleet vehicles.

The core purpose is to programmatically drive the web application to:
1.  Log in.
2.  Look up a vehicle by its MVA (Motor Vehicle Number).
3.  Inspect and manage **Work Items** and **Complaints** associated with the vehicle.
4.  Specifically, it automates the process of handling "PM" (Preventive Maintenance) tasks, either by associating existing PM complaints or creating new ones.

The project follows a structured design pattern, likely a variation of the **Page Object Model (POM)**, with clear separation of concerns:
*   **`core`**: Manages the WebDriver instance (`driver_manager.py`) and base test configurations.
*   **`pages`**: Contains classes representing different pages/views of the PWA (e.g., `LoginPage`, `MVAInputPage`).
*   **`flows`**: Encapsulates multi-step business logic and user workflows (e.g., `complaints_flows.py`, `work_item_flow.py`).
*   **`tests`**: Contains the `pytest` test suites that orchestrate the automation.
*   **`utils`**: Provides helper functions for UI interactions, data loading, and logging.
*   **`config`**: Manages environment-specific configuration like credentials.

## Application Flow

```
[MVA] → [Work Items?]
   ├─ Open PM → Complete → Done
   ├─ Complete <30 days → Skip
   └─ Else → New Work Item → Complaint → Mileage → Opcode → Complete
```

## Building and Running

### Dependencies
*   Python 3.13+
*   Selenium WebDriver
*   Pytest
*   (A `requirements.txt` is mentioned in the documentation but not present in the file listing).

### Setup
1.  **WebDriver**: Ensure `msedgedriver.exe` corresponding to your installed Edge browser version is placed in the project root (`C:\temp\Python`). The `core/driver_manager.py` script contains logic to verify version compatibility.
2.  **Configuration**: Edit `config/config.json` to provide valid credentials (`username`, `password`, `login_id`).
3.  **Test Data**: The main test expects a `data/mva.csv` file containing a list of MVA numbers to process.

### Running the Automation

There are two ways to run the project:

1.  **As a Standalone Script:**
    This executes the main login sequence defined in `run_compass.py`.
    ```bash
    py run_compass.py
    ```

2.  **As a Pytest Suite:**
    This runs the end-to-end test flow defined in `tests/test_mva_complaints_tab_fixed.py`.
    ```bash
    pytest -q -s tests/test_mva_complaints_tab_fixed.py
    ```
    You can also run specific markers, like the `smoke` test:
    ```bash
    pytest -m smoke
    ```

## Development Conventions

*   **Code Style**: The code generally follows PEP 8, with a `.flake8` configuration file present.
*   **Modularity**: Functionality is broken down into logical modules. UI interactions are abstracted in `utils/ui_helpers.py`, and application-specific workflows are in the `flows` directory.
*   **Page Object Pattern**: The `pages` directory contains classes that model the pages of the application, encapsulating the locators and actions for that page.
*   **Configuration Management**: All hardcoded secrets and environment-specific settings are externalized to `config/config.json` and loaded via `config/config_loader.py`.
*   **Testing**: `pytest` is the test runner. Tests are located in the `tests` directory. The `core/base_test.py` file defines a `driver` fixture that handles setup and teardown of the WebDriver for each test.
*   **Logging**: The project uses the standard `logging` module. A logger named `mc.automation` is configured and used throughout the application.
*   **Error Handling**: The code uses `try...except` blocks to handle potential Selenium exceptions (e.g., `TimeoutException`, `StaleElementReferenceException`) and logs errors gracefully. UI interaction helpers in `ui_helpers.py` often return a boolean status.
*   **TODO Conventions**: Use `[TODO]` inline markers.
*   **Logging Strategy**:
    *   **Levels**: DEBUG (verbose), INFO (normal), WARN (unexpected but handled), ERROR (failures)
    *   **Tags**: [LOGIN], [MVA], [WORKITEM], [COMPLAINT], [WARN], [ERROR]
    *   **Format**: [TAG] {mva} - action/outcome
*   **Weekly Review**:
    *   ✅ Confirm branch hygiene (main vs feature)
    *   ✅ Check recent commits for scope creep
    *   ✅ Update History.md with milestones
    *   ✅ Archive noisy details into Session_Log.md