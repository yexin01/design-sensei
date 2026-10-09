# Security policy

## Reporting a vulnerability

Please report security problems privately through GitHub's "Report a vulnerability" feature on this repository (Security tab), not in a public issue. Include what you found, how to reproduce it and the affected version. Expect an acknowledgement within a few days.

## What Design Sensei does that matters for security

* It runs `git` to download repositories you ask it to. Only `https://` URLs from `catalog/sources.yaml` are cloned. It never runs a hook, install script, submodule update or LFS download from a downloaded repository, never executes downloaded code, and never follows symlinks while indexing.
* Downloads happen in a temporary directory and are moved into place only on success; checkouts with local changes are never modified.
* It does not send data anywhere: there is no telemetry, server or API call. Network access is limited to `git` talking to the hosts in the catalog, and only for `setup`/`sources sync`/`doctor --online`.
* The skill pre-approves only read-only commands (`search`, `doctor`, `sources list|show|status`, `config show`, `eval`). Commands that download or write (`setup`, `sources sync`, `index build`, `licenses scan --write`) still ask for permission.
* Treat downloaded upstream code like any untrusted third-party code: read it before running anything from it.

## Supported versions

Only the latest release receives fixes while the project is below 1.0.
