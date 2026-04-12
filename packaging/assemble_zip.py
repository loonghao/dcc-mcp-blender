"""Assemble a Blender addon ZIP package for dcc-mcp-blender.

This script:
1. Resolves the latest compatible dcc-mcp-core version from PyPI
2. Downloads the appropriate platform wheel(s)
3. Bundles the dcc_mcp_blender package + dcc-mcp-core into a Blender addon ZIP
4. Produces a file named ``dcc_mcp_blender_addon_{platform}_v{version}.zip``

Usage::

    python packaging/assemble_zip.py --platform win64 --output-dir dist_addon/
    python packaging/assemble_zip.py --platform linux --output-dir dist_addon/
    python packaging/assemble_zip.py --platform macos --output-dir dist_addon/
"""

from __future__ import annotations

import argparse
import io
import os
import pathlib
import re
import shutil
import sys
import tempfile
import urllib.request
import zipfile

# ── configuration ─────────────────────────────────────────────────────────────

PACKAGE_ROOT = pathlib.Path(__file__).parent.parent
SRC_DIR = PACKAGE_ROOT / "src" / "dcc_mcp_blender"
PYPROJECT = PACKAGE_ROOT / "pyproject.toml"

MIN_CORE_VERSION = "0.12.18"
CORE_PACKAGE = "dcc-mcp-core"

# Platform → Python ABI tag (Blender 4.x ships Python 3.11+)
PLATFORM_PYTHON = {
    "win64": [("cp311-cp311-win_amd64", "3.11"), ("cp310-cp310-win_amd64", "3.10")],
    "linux": [("cp311-cp311-linux_x86_64", "3.11"), ("cp310-cp310-linux_x86_64", "3.10")],
    "macos": [("cp311-cp311-macosx_10_15_x86_64", "3.11"), ("cp311-cp311-macosx_11_0_arm64", "3.11")],
}

PYPI_URL = "https://pypi.org/pypi/{package}/json"


# ── helpers ────────────────────────────────────────────────────────────────────


def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        import json

        return json.loads(resp.read())


def resolve_core_version(min_version: str = MIN_CORE_VERSION) -> str:
    """Return the latest dcc-mcp-core version >= min_version."""
    data = _fetch_json(PYPI_URL.format(package=CORE_PACKAGE))
    from packaging.version import Version

    available = [Version(v) for v in data["releases"].keys() if not Version(v).is_prerelease]
    min_ver = Version(min_version)
    compatible = [v for v in available if v >= min_ver and v < Version("1.0.0")]
    if not compatible:
        raise RuntimeError(f"No compatible {CORE_PACKAGE} release found (>={min_version},<1.0.0)")
    best = sorted(compatible)[-1]
    print(f"Resolved {CORE_PACKAGE} version: {best}")
    return str(best)


def download_core_wheels(version: str, platform: str, dest_dir: pathlib.Path) -> list[pathlib.Path]:
    """Download dcc-mcp-core wheel(s) for the given platform."""
    data = _fetch_json(PYPI_URL.format(package=CORE_PACKAGE))
    release_files = data["releases"].get(version, [])

    abi_patterns = PLATFORM_PYTHON.get(platform, [])
    # Also accept any3 / abi3 wheels (py3-none-any or cp3X-abi3)
    generic_patterns = ["py3-none-any", "py310-none-any", "py311-none-any"]

    downloaded: list[pathlib.Path] = []
    dest_dir.mkdir(parents=True, exist_ok=True)

    for file_info in release_files:
        filename = file_info["filename"]
        if not filename.endswith(".whl"):
            continue

        matched = any(pat in filename for pat, _ in abi_patterns)
        generic_match = any(p in filename for p in generic_patterns)

        if matched or generic_match:
            url = file_info["url"]
            dest = dest_dir / filename
            if not dest.exists():
                print(f"  Downloading: {filename}")
                urllib.request.urlretrieve(url, dest)  # noqa: S310
            else:
                print(f"  Cached: {filename}")
            downloaded.append(dest)

    if not downloaded:
        print(f"  Warning: no wheels found for platform '{platform}', skipping core bundling")
    return downloaded


def extract_wheel(wheel_path: pathlib.Path, dest_dir: pathlib.Path) -> None:
    """Extract a wheel into dest_dir, skipping .dist-info."""
    with zipfile.ZipFile(wheel_path, "r") as zf:
        for member in zf.namelist():
            if ".dist-info/" in member:
                continue
            zf.extract(member, dest_dir)


def get_package_version() -> str:
    """Read version from pyproject.toml."""
    text = PYPROJECT.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise RuntimeError("Could not find version in pyproject.toml")
    return m.group(1)


def assemble(platform: str, output_dir: pathlib.Path) -> pathlib.Path:
    """Assemble the addon ZIP for the given platform.

    Returns the path to the created ZIP file.
    """
    version = get_package_version()
    zip_name = f"dcc_mcp_blender_addon_{platform}_v{version}.zip"
    zip_path = output_dir / zip_name

    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        addon_dir = tmp_dir / "dcc_mcp_blender"
        addon_dir.mkdir()

        # 1) Copy dcc_mcp_blender package source
        print("Copying dcc_mcp_blender package...")
        shutil.copytree(SRC_DIR, addon_dir / "dcc_mcp_blender")

        # 2) Download and extract dcc-mcp-core
        print(f"Resolving {CORE_PACKAGE}...")
        try:
            core_version = resolve_core_version()
            wheels_dir = tmp_dir / "wheels"
            wheels = download_core_wheels(core_version, platform, wheels_dir)
            for wheel in wheels:
                print(f"  Extracting {wheel.name}...")
                extract_wheel(wheel, addon_dir)
        except Exception as e:
            print(f"Warning: could not bundle dcc-mcp-core: {e}")

        # 3) Write __init__.py for Blender addon registration
        _write_addon_init(addon_dir, version)

        # 4) Zip everything
        print(f"Creating {zip_name}...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in addon_dir.rglob("*"):
                if file.is_file() and "__pycache__" not in str(file):
                    arcname = file.relative_to(tmp_dir)
                    zf.write(file, arcname)

    print(f"Created: {zip_path}")
    return zip_path


def _write_addon_init(addon_dir: pathlib.Path, version: str) -> None:
    """Write a Blender-compatible __init__.py at the addon root."""
    init_path = addon_dir / "__init__.py"
    # Only overwrite if it doesn't already have bl_info
    existing = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
    if "bl_info" in existing:
        return

    major, minor, patch = version.split(".")[:3]
    content = f'''"""Blender Addon: DCC MCP Blender.

Auto-generated addon entry point — wraps dcc_mcp_blender.
"""

import sys
import os

# Ensure the addon directory is on sys.path so bundled packages are importable
_addon_dir = os.path.dirname(__file__)
if _addon_dir not in sys.path:
    sys.path.insert(0, _addon_dir)

bl_info = {{
    "name": "DCC MCP Blender",
    "author": "Long Hao",
    "version": ({major}, {minor}, {patch}),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > DCC MCP",
    "description": "Embeds an MCP HTTP server directly inside Blender for AI-driven 3D workflows",
    "category": "System",
    "doc_url": "https://github.com/loonghao/dcc-mcp-blender",
    "tracker_url": "https://github.com/loonghao/dcc-mcp-blender/issues",
}}


def register():
    """Start the MCP server when the addon is enabled."""
    try:
        from dcc_mcp_blender.server import start_server
        start_server()
        print("[DCC MCP Blender] Server started on http://127.0.0.1:8765/mcp")
    except Exception as e:
        print(f"[DCC MCP Blender] Failed to start server: {{e}}")


def unregister():
    """Stop the MCP server when the addon is disabled."""
    try:
        from dcc_mcp_blender.server import stop_server
        stop_server()
        print("[DCC MCP Blender] Server stopped")
    except Exception as e:
        print(f"[DCC MCP Blender] Failed to stop server: {{e}}")
'''
    init_path.write_text(content, encoding="utf-8")


# ── CLI ────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble Blender addon ZIP for dcc-mcp-blender")
    parser.add_argument(
        "--platform",
        choices=list(PLATFORM_PYTHON.keys()),
        default="linux",
        help="Target platform (default: linux)",
    )
    parser.add_argument(
        "--output-dir",
        default="dist_addon",
        help="Output directory for the ZIP file (default: dist_addon/)",
    )
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    zip_path = assemble(platform=args.platform, output_dir=output_dir)
    print(f"\nDone: {zip_path}")


if __name__ == "__main__":
    main()
