@echo off
REM Run all config_center tests with pytest
REM Usage: run_tests.bat [--verbose] [--cov]

echo ====================================
echo Running config_center tests
echo ====================================

setlocal

REM Install test dependencies if needed
echo Installing test dependencies...
pip install pytest pytest-asyncio pytest-cov httpx python-jose[cryptography] jsonschema

echo.
echo Running tests...

if "%1"=="--cov" (
    pytest tests/test_config_center/ -v --cov=taolib.config_center --cov-report=term-missing
) else if "%1"=="--verbose" (
    pytest tests/test_config_center/ -v
) else (
    pytest tests/test_config_center/ -v --tb=short
)

echo.
echo ====================================
echo Test run complete
echo ====================================
