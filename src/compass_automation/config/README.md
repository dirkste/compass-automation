# Configuration reference (`config.json`)

This project reads runtime configuration from:

- `src/compass_automation/config/config.json`
- Loaded at import-time by `src/compass_automation/config/config_loader.py` via `get_config("...")`

## Key reference

### Credentials

- `username` (string)
  - Login email/UPN.
- `password` (string)
  - Login password.
- `login_id` (string)
  - Identifier used in the app after SSO (e.g. employee id / WWID / login id).

### Timing

- `delay_seconds` (number)
  - Default UI wait/timeout value used in various flows.
  - Code typically reads this via `get_config(...)` or `DEFAULT_TIMEOUT`.

### Logging (Two-Vector)

## The “Microscope” approach (recommended)

This project’s verbosity levels are intended to act like a **multi-resolution microscope**:

- `MIN` = **Surface** (“What happened?”)
  - Use for clean, scannable outcome statements.
  - Examples: success/fail, completed/skip, one-line summary.

- `MED` = **Structure** (“How did we decide?”)
  - Use for decision-path breadcrumbs: key branches, gates, retries.
  - Examples: which branch was taken, retry #, chosen strategy.

- `FULL` = **Atomic** (“Why exactly?”)
  - Use for forensic details: raw values, payloads, DOM snippets, variable dumps.
  - Examples: exact locator text, response bodies, serialized state.

The key idea is: keep most logs at `MIN`/`MED`, and reserve `FULL` for the specific component you’re troubleshooting.

The logging system is configured by **two independent knobs**:

- **Minimum Criticality** (importance floor): only log if `record.level >= min_crit`
- **Maximum Verbosity** (detail ceiling): only log if `record.verbosity <= max_verb`

These map to `src/compass_automation/utils/logger.py`.

#### Keys

- `logging.min_crit` (string | int)
  - Minimum criticality to emit.
  - Typical string values: `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`.
  - If set to `"INFO"`, `DEBUG` logs are dropped.

- `logging.max_verb` (string)
  - Maximum verbosity to emit. Allowed values:
    - `"MIN"` (least detail)
    - `"MED"` (default)
    - `"FULL"` (most detail)

  Microscope mapping:
  - `MIN` = Surface
  - `MED` = Structure
  - `FULL` = Atomic

- `logging.file` (string)
  - File path for the file handler. Defaults to `automation.log`.

#### Output format

- Session header (printed once at initialization):
  - `=== Log Session Started: YYYY-MM-DD ===`

- Per-line header:
  - `[HH:MM:SS][CRIT_VERB][Source][Context]<Message>`

Where:
- `CRIT` is one of: `INF`, `WRN`, `ERR`, `FTL`
- `VERB` is one of: `MIN`, `MED`, `FULL`
- `Source` is a logical component (e.g. `DRIVER`, `NAV`, `LOGIN`).
  - If not explicitly set, it is inferred from message prefixes like `[DRIVER] ...`.
  - If it can’t be inferred, it falls back to `APP`.
- `Context` is the calling function name (not filename).

#### Legacy keys (backwards compatibility)

These are kept so older code/tests don’t break, but they are **not the primary controls** anymore:

- `logging.level`
  - Used only as a fallback if `logging.min_crit` is absent.
- `logging.format`
  - Not used by the Two-Vector formatter.

#### Example configs

Quiet-ish logs (recommended default):

```json
"logging": {
  "min_crit": "INFO",
  "max_verb": "MED",
  "file": "automation.log"
}
```

Verbose debugging (shows DEBUG + FULL):

```json
"logging": {
  "min_crit": "DEBUG",
  "max_verb": "FULL",
  "file": "automation.log"
}
```

Targeted “microscope” usage pattern (recommended for troubleshooting)

- Default config stays clean:
  - `min_crit = INFO`
  - `max_verb = MED`

- In code, only the area under the lens emits `FULL`:
  - Use `TwoVectorLogger(...).info_v(Verbosity.FULL, "...")` (or `debug`/`error` equivalents)
  - Then temporarily raise `logging.max_verb` to `FULL` when you need those details.

#### Code examples (recommended patterns)

Efficient logging (avoids string interpolation when filtered out):

```python
from compass_automation.utils.logger import TwoVectorLogger, Verbosity, log

driver_log = TwoVectorLogger(log, source="DRIVER")

# Surface (MIN): outcome
driver_log.info_v(Verbosity.MIN, "Driver started")

# Structure (MED): decision path
driver_log.warning_v(Verbosity.MED, "Retrying click (%s/%s)", attempt, max_attempts)

# Atomic (FULL): forensic values
driver_log.info_v(Verbosity.FULL, "Locator=%r; url=%s", locator, current_url)
```

Important: if you use f-strings (e.g. `f"x={x}"`), the string is built even if the message is filtered.
Prefer `"...%s"` + args for expensive values.

### Performance

- `performance.config_threshold` (number)
  - Threshold used by performance tooling/benchmarks.
- `performance.object_creation_threshold` (number)
  - Threshold used by performance tooling/benchmarks.
