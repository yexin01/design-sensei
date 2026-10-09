"""Thin, defensive wrappers around the ``git`` command line.

Safety properties relied on by the sync tool:
  * never prompts for credentials (``GIT_TERMINAL_PROMPT=0``), never smudges LFS
  * never runs hooks from the repository being managed (``core.hooksPath=/dev/null``)
  * never initializes submodules and never runs any script from a downloaded repository
  * every network operation can be retried on transient failures
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from typing import Callable, Dict, List, Optional, Sequence, TypeVar

T = TypeVar("T")

DEFAULT_TIMEOUT = int(os.environ.get("DESIGN_SENSEI_GIT_TIMEOUT", "900"))

_TRANSIENT_MARKERS = (
    "could not resolve host",
    "connection reset",
    "connection timed out",
    "operation timed out",
    "timed out",
    "early eof",
    "rpc failed",
    "the remote end hung up",
    "unable to access",
    "tls",
    "ssl",
    "http 500",
    "http 502",
    "http 503",
    "http 504",
    "returned error: 5",
    "temporary failure",
    "network is unreachable",
    "failed to connect",
)
_NOT_FOUND_MARKERS = ("repository not found", "not found", "does not appear to be a git repository", "could not read from remote")
_AUTH_MARKERS = ("authentication failed", "terminal prompts disabled", "permission denied", "could not read username")


class GitError(RuntimeError):
    def __init__(self, message: str, returncode: int = 1, stderr: str = "", kind: str = "git_error"):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr
        self.kind = kind  # network | not_found | auth | timeout | git_error | missing_git


def git_executable() -> Optional[str]:
    return shutil.which("git")


def git_version() -> Optional[str]:
    exe = git_executable()
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def classify_error(stderr: str) -> str:
    low = stderr.lower()
    if any(m in low for m in _AUTH_MARKERS):
        return "auth"
    if any(m in low for m in _TRANSIENT_MARKERS):
        return "network"
    if any(m in low for m in _NOT_FOUND_MARKERS):
        return "not_found"
    return "git_error"


def _env() -> Dict[str, str]:
    env = dict(os.environ)
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
        "GIT_ASKPASS": "true",
        "GCM_INTERACTIVE": "never",
        "LC_ALL": "C",
    })
    return env


def run_git(args: Sequence[str], cwd: Optional[str] = None, timeout: Optional[int] = None, check: bool = True) -> "subprocess.CompletedProcess[str]":
    """Run ``git`` with safe defaults. Raises GitError on failure when ``check`` is true."""
    exe = git_executable()
    if not exe:
        raise GitError("git is not installed or not on PATH", 127, "", "missing_git")
    cmd = [exe, "-c", "core.hooksPath=/dev/null", "-c", "advice.detachedHead=false", "-c", "gc.auto=0"] + list(args)
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout or DEFAULT_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitError("git %s timed out after %ss" % (args[0], exc.timeout), 124, "", "timeout")
    except OSError as exc:
        raise GitError("could not run git: %s" % exc, 127, "", "missing_git")
    if check and proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        raise GitError("git %s failed: %s" % (args[0], stderr.splitlines()[-1] if stderr else "exit %d" % proc.returncode), proc.returncode, stderr, classify_error(stderr))
    return proc


def with_retries(fn: Callable[[], T], attempts: int = 3, base_delay: float = 1.5, sleep: Callable[[float], None] = time.sleep) -> T:
    """Retry ``fn`` on transient network ``GitError`` values with exponential back-off."""
    last = None  # type: Optional[GitError]
    for attempt in range(attempts):
        try:
            return fn()
        except GitError as exc:
            last = exc
            if exc.kind not in ("network", "timeout") or attempt == attempts - 1:
                raise
            sleep(base_delay * (2 ** attempt))
    assert last is not None
    raise last


def ls_remote(url: str, ref: str = "HEAD", attempts: int = 3) -> Optional[str]:
    """Resolve ``ref`` on the remote to a commit hash (None when the ref does not exist)."""
    def op() -> Optional[str]:
        out = run_git(["ls-remote", url, ref], timeout=120).stdout
        for line in out.splitlines():
            sha, _, name = line.partition("\t")
            if re.match(r"^[0-9a-f]{40}$", sha):
                return sha
        return None
    return with_retries(op, attempts=attempts)


def is_repo(path: str) -> bool:
    return os.path.exists(os.path.join(path, ".git"))


def head_commit(path: str) -> Optional[str]:
    try:
        out = run_git(["rev-parse", "HEAD"], cwd=path, timeout=60).stdout.strip()
    except GitError:
        return None
    return out if re.match(r"^[0-9a-f]{40}$", out) else None


def remote_url(path: str) -> Optional[str]:
    try:
        return run_git(["config", "--get", "remote.origin.url"], cwd=path, timeout=60).stdout.strip() or None
    except GitError:
        return None


def tracked_changes(path: str) -> List[str]:
    """Modified/deleted/staged tracked files (untracked files are never a problem for sync)."""
    out = run_git(["status", "--porcelain", "--untracked-files=no"], cwd=path, timeout=300).stdout
    return [line for line in out.splitlines() if line.strip()]


def has_commit(path: str, sha: str) -> bool:
    proc = run_git(["cat-file", "-e", "%s^{commit}" % sha], cwd=path, timeout=60, check=False)
    return proc.returncode == 0


def sparse_list(path: str) -> List[str]:
    proc = run_git(["sparse-checkout", "list"], cwd=path, timeout=60, check=False)
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip()) if proc.returncode == 0 else []


def normalize_url(url: str) -> str:
    """Compare-friendly form of a git URL (case-insensitive host/path, no .git, no trailing slash)."""
    u = url.strip().lower().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    return u.rstrip("/")
