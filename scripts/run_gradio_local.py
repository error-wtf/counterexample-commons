#!/usr/bin/env python3
"""Launch the Counterexample Commons Gradio UI locally."""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import build_app  # noqa: E402
from counterexample_commons.config import AppMode  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Counterexample Commons — Local Gradio UI",
    )
    parser.add_argument(
        "--mode",
        default="local-private",
        choices=[
            "local-private",
            "local-share",
            "public-demo",
            "colab-private",
            "colab-public-demo",
            "hosted-public-demo",
        ],
        help="Execution mode (default: local-private)",
    )
    parser.add_argument(
        "--port", type=int, default=7860,
        help="Port (default: 7860)",
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="Don't auto-open browser",
    )
    parser.add_argument(
        "--confirm-public-share", action="store_true",
        help="Required to enable a public share link",
    )
    args = parser.parse_args()

    mode = AppMode(args.mode)
    share = args.confirm_public_share

    _private_modes = {AppMode.LOCAL_PRIVATE, AppMode.COLAB_PRIVATE}
    if share and mode in _private_modes:
        raise SystemExit(
            f"Refusing public share: '{mode.value}' may load secrets or "
            "writable research state. Use a public-demo mode instead."
        )

    demo = build_app(mode=mode)
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=args.port,
        share=share,
        inbrowser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
