def format_universe_validate_success(path: str) -> str:
    """Format success message for universe validation."""
    return f"Success: Universe validated successfully: {path}"


def format_universe_diagnostics_success(path: str) -> str:
    """Format success message for diagnostics report."""
    return f"Success: Diagnostics report written to: {path}"


def format_universe_error(message: str) -> str:
    """Format error message."""
    return f"Error: {message}"
