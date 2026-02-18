"""Run the Next-Gen Deep Research FastAPI backend.

This script loads the backend `app.py` by file path (works even though the
workspace contains a hyphenated folder name) and starts uvicorn with the
ASGI `app` object.

Usage:
  python run.py --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import uvicorn


def load_app_from_path(path: Path):
    spec = importlib.util.spec_from_file_location("backend_app", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    if not hasattr(module, "app"):
        raise RuntimeError(f"Module {path} does not expose `app` ASGI object")
    return getattr(module, "app")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn auto-reload")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent
    backend_path = project_root / "nextgen-research-app" / "backend" / "app.py"
    if not backend_path.exists():
        print(f"Could not find backend app at {backend_path}")
        return 2

    app = load_app_from_path(backend_path)

    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
