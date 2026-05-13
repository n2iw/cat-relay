# How to Contribute

Thank you for helping improve Cat-Relay. This document focuses on **adding or changing device clients** (the code that talks to SDR and radio-control software). General fixes and documentation are welcome too; when in doubt, open an issue or a small pull request so we can discuss the change.

## Run the project from source

See the [README](README.md#run-from-source-code) for Python version, dependencies, and commands (`uv run src/app.py` or `python3 src/app.py` from the repository root).

## The `BaseClient` contract

Every client that syncs frequency and mode with the relay must subclass `BaseClient` in `src/clients/base_client.py` and implement its abstract API. The relay uses **async** I/O and manages clients with `async with`, so your class must be a proper **async context manager**.

### Constructor

Implement:

```python
def __init__(self, ip: str, port: int, name: str) -> None
```

Store `ip`, `port`, and `name` as needed. The `name` argument identifies which registry entry created the client (for example the display name of the SDR or CAT software).

### Async context manager

- **`async def __aenter__(self)`** — Open connections to the device or service (TCP, HTTP, and so on). Return `self` (or a compatible handle; existing clients return `self`).
- **`async def __aexit__(self, exc_type, exc_val, exc_tb)`** — Close connections and release resources.

The main loop in `src/cat_relay.py` enters both CAT and SDR clients this way before syncing.

### Frequency and mode

- **`async def get_freq(self) -> int`** — Return the current frequency in **hertz** as an integer.

- **`async def get_mode(self) -> CoreMode`** — Return the current mode as a **`CoreMode`** enum value (`FM`, `AM`, `USB`, `LSB`, `CW`, or `NOT_SUPPORTED`). Do **not** return the device’s native mode string; map native modes to `CoreMode` first.

- **`async def set_freq_mode(self, freq: int, mode: CoreMode) -> None`** — Apply `freq` (hertz) and `mode` on the device. The `mode` argument is always a **core** mode; translate to the wire protocol your software expects.

### `CoreMode` semantics

`CoreMode` is the shared vocabulary between CAT and SDR sides:

- All modes passed into and returned from these methods should be **core** modes unless you are doing an internal native-to-core mapping inside your client.
- Use **`CoreMode.NOT_SUPPORTED`** when the device reports a mode that does not map to any other core mode. The relay may fall back to the last known good mode when syncing.
- Prefer **not** sending redundant mode changes to the device: if your client tracks the last set core mode, avoid overwriting the device when the requested mode matches what you already applied (see comments in `base_client.py`).

### `DataNotAvailableException`

Raise **`DataNotAvailableException`** from `src/clients/base_client.py` when frequency or mode cannot be read **temporarily** (for example a transient parse failure or empty response). The sync loop catches this, logs, and skips that cycle instead of tearing down the whole relay.

## Mode mapping helper

Many clients use **`ModeMapper`** in `src/clients/utils/mode_mapper.py` to translate between native mode strings and `CoreMode`. Provide:

- A **native → core** map for `get_mode`.
- An optional **core → native** map for `set_freq_mode` when the default mapping is not enough.

Unmapped native modes log a warning; the default mapper behavior should be understood before relying on it in production.

## Tests and manual checks

Exercise `get_freq` / `get_mode` and `set_freq_mode` against real or mocked endpoints, and confirm Settings defaults and fixed-port behavior if applicable.

## Registering a new client

Software display names, the Settings dropdown lists, and the client class mapping all live in **`src/clients/client_registry.py`**. Wire a new client there first; other files consume that module.

**`src/clients/client_registry.py`**
   - Add a **string constant** for the software name (the exact label shown in Settings, for example `MY_APP = 'My App'`).
   - Append that constant to **`VALID_SDRS`** and/or **`VALID_CAT_SOFTWARE`** so it appears in the correct dropdown (`src/settings.py` imports those lists from here).
   - Import your **`BaseClient`** subclass and add a **`Registry`** entry to **`client_registry`**. The dict **key** must be the same string as the constant value (and as `Registry.name`). Set:
     - **`name`** — Same string as the key (display/software name passed into your client’s `name` argument).
     - **`default_port`** — Default port shown in Settings when the user selects this software.
     - **`fixed_port`** — `True` if the port field should be disabled (for example a fixed vendor port); `False` if the user may edit it.
     - **`client_class`** — Your `BaseClient` subclass.


Existing clients such as `src/clients/hamlib.py`, `src/clients/flrig.py`, and `src/clients/sdr_connect.py` are good references for structure and error handling.

## Pull requests

- Keep changes focused and match surrounding style (imports, logging, typing).
- If you add a client, include enough detail in the PR description for reviewers to understand the protocol and how you tested it.

We appreciate your contributions.
