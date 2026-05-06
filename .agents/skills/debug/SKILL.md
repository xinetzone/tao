---
name: debug
description:
  Investigate test failures, service errors, and runtime issues by tracing logs
  and correlating request identifiers; use when tests fail unexpectedly, services
  crash, or errors need root-cause analysis.
---

# Debug

## Goals

- Find why a test, service, or workflow is failing.
- Correlate request identifiers across distributed components quickly.
- Read the right logs in the right order to isolate root cause.

## Log Sources

- Application logs: structured JSON logs via `structlog`
  - Configured in `src/taolib/testing/logging_config.py`
  - Default output: stderr (dev) or JSON stdout (production)
- Service logs: `uvicorn` access logs + application logs
  - Each service module (auth, config, data_sync, etc.) logs under its own namespace
- Test output: `pytest` verbose output with `--tb=short` or `--tb=long`

## Correlation Keys

- `request_id`: unique per HTTP request (set by middleware)
- `trace_id`: distributed tracing identifier (when tracing is enabled)
- `session_id`: user session or API key context
- `task_id`: background task identifier (task queue module)

Use these fields as join keys when correlating logs across services.

## Quick Triage (Test Failure)

1. Identify the failing test module and function name from pytest output.
2. Check if the failure is consistent (reproducible) or flaky (intermittent).
3. Look at the traceback — identify whether the failure is in:
   - Test setup/fixture (conftest.py issues, missing mocks)
   - Business logic (code under test)
   - Integration layer (database, Redis, external API)
4. Run the single failing test in isolation first:
   ```bash
   pytest tests/path/to/test_file.py::test_function -v --tb=long
   ```

## Quick Triage (Service Error)

1. Check service health and recent logs.
2. Identify the failing component (FastAPI route, background worker, database query).
3. Extract `request_id` from error logs to trace the full request lifecycle.
4. Check for common patterns:
   - Connection refused: service dependency not running
   - Timeout: slow database/API query or deadlock
   - Auth error: expired token, invalid credentials
   - Validation error: schema mismatch, missing fields

## Commands

```bash
# 1) Run a single failing test with full traceback
pytest tests/path/to/test_file.py::test_function -v --tb=long

# 2) Run tests with stdout/stderr capture disabled (see print output)
pytest tests/path/to/test_file.py -v -s

# 3) Search structured logs for a specific request
rg "request_id=<id>" var/log/*.log

# 4) Search for error-level logs across all services
rg '"level":\s*"error"' var/log/*.log

# 5) Check for connection errors (database, Redis)
rg "ConnectionRefusedError|ConnectionError|timeout" var/log/*.log

# 6) Trace a specific task through the task queue
rg "task_id=<id>" var/log/*.log

# 7) Check FastAPI/uvicorn access logs for HTTP errors
rg '"status_code":\s*(4|5)\d{2}' var/log/*.log
```

## Steps

1. Identify the failure type: test failure, service error, or runtime crash.
2. Locate the relevant logs or test output.
3. Extract correlation keys (`request_id`, `trace_id`, `task_id`) from the error.
4. Trace the request/session lifecycle from start to failure.
5. Classify the root cause: logic, integration, auth, concurrency, or configuration.
6. Reproduce the issue locally if possible.
7. Implement the fix and validate with tests.

## Investigation Flow

1. **Locate the failure:**
    - For tests: identify from pytest output or CI logs.
    - For services: check health endpoints, error log files, or structured log output.
2. **Establish timeline:**
    - Find the first error or warning in the relevant time window.
    - Correlate with deployment or configuration changes if applicable.
3. **Classify the problem:**
    - **Logic error:** incorrect business logic, wrong calculation, missing validation.
    - **Integration error:** database connection, Redis timeout, external API failure.
    - **Auth error:** token expired, insufficient permissions, invalid credentials.
    - **Concurrency error:** race condition, deadlock, stale cache.
    - **Configuration error:** missing env var, wrong TOML/YAML setting, schema mismatch.
4. **Validate scope:**
    - Is the failure isolated to one endpoint/test or affecting multiple?
    - Can you reproduce it locally with the same inputs?
5. **Capture evidence:**
    - Save relevant log lines with timestamps, `request_id`, and `trace_id`.
    - Record the failing test name, input data, and expected vs actual behavior.
    - Note the probable root cause and the exact failing stage.

## Debugging FastAPI Services

When a FastAPI endpoint is failing:

1. Enable debug logging:
   ```python
   import structlog
   structlog.configure(wrapper_class=structlog.make_filtering_bound_logger("DEBUG"))
   ```
2. Use the test client for local reproduction:
   ```python
   from fastapi.testclient import TestClient
   from taolib.testing.auth.server.app import app
   client = TestClient(app)
   response = client.get("/endpoint")
   ```
3. Check request/response lifecycle:
   - Middleware processing (auth, rate limiting, logging)
   - Route handler execution
   - Database query execution
   - Response serialization
4. For SQLite `:memory:` issues in tests, ensure `StaticPool` is used:
   ```python
   from sqlalchemy.pool import StaticPool
   engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
   ```

## Debugging Async Issues

For `asyncio`-related failures:

1. Enable asyncio debug mode:
   ```bash
   PYTHONASYNCIODEBUG=1 pytest tests/ -v
   ```
2. Check for common async pitfalls:
   - Unawaited coroutines (missing `await`)
   - Event loop closure in tests
   - Thread safety with shared state
3. Use `pytest-asyncio` with `auto` mode (configured in `pyproject.toml`).

## Notes

- Prefer `rg` over `grep` for speed on large logs.
- Structured JSON logs can be piped through `jq` for filtering:
  ```bash
  cat var/log/app.log | jq 'select(.level == "error")'
  ```
- For database-related issues, check MongoDB connection strings and Redis host/port in
  the service configuration.
- If a test passes locally but fails in CI, check for environment differences
  (Python version, OS, dependency versions, env vars).
- For FastAPI TestClient + SQLite issues, always use `StaticPool` to share the
  in-memory database across threads.
