"""Hugging Face Spaces entry point — public demo mode only."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.main import build_app  # noqa: E402
from counterexample_commons.config import AppMode  # noqa: E402

demo = build_app(mode=AppMode.COLAB_PUBLIC_DEMO)
demo.queue().launch()
