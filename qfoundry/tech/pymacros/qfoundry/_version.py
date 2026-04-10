# This file is part of QFoundry PDK.
# Version is resolved at runtime using the following priority:
#   1. Package metadata (when installed via pip)
#   2. git describe (when running directly from a git clone)
#   3. "unknown" fallback

def _get_version():
    # 1. Try installed package metadata (pip install / editable install)
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("qfoundry-pdk")
        except PackageNotFoundError:
            pass
    except ImportError:
        pass

    # 2. Fall back to git describe (works in any git clone)
    try:
        import subprocess
        import os
        # Navigate up from qfoundry/tech/pymacros/qfoundry/ to the repo root
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        result = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return "unknown"


__version__ = _get_version()
