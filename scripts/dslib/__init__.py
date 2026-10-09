"""Shared, standard-library-only helpers for the Design Sensei tooling."""

__version__ = "0.1.0"

# Exit codes shared by every CLI command (documented in README.md).
EXIT_OK = 0
EXIT_FAILURE = 1  # validation errors, failed operation, unhealthy doctor report
EXIT_USAGE = 2  # bad command line (argparse uses this code too)
EXIT_PARTIAL = 3  # some items succeeded, some failed (for example source sync)
EXIT_ENVIRONMENT = 4  # a required tool or network is unavailable
