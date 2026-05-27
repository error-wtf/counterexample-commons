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
    parser.add_argument(
        "--confirm-live-ai-share", action="store_true",
        help="Required to share a local-private live-AI session",
    )
    args = parser.parse_args()

    mode = AppMode(args.mode)
    share = args.confirm_public_share or args.confirm_live_ai_share

    _private_modes = {AppMode.LOCAL_PRIVATE, AppMode.COLAB_PRIVATE}
    if args.confirm_public_share and mode in _private_modes:
        raise SystemExit(
            f"Refusing public share: '{mode.value}' may load secrets or "
            "writable research state. Use a public-demo mode instead."
        )
    if args.confirm_live_ai_share and mode != AppMode.LOCAL_PRIVATE:
        raise SystemExit(
            "--confirm-live-ai-share is only valid with local-private mode."
        )
    if args.confirm_live_ai_share:
        print("WARNING - SHARED LIVE AI SESSION")
        print()
        print(
            "This running Gradio session may send real requests to "
            "configured AI providers."
        )
        print(
            "Anyone with access to the shared URL may be able to trigger "
            "API requests, consume quota or incur cost."
        )
        print("Provider keys are not displayed or exported.")
        print()

    demo = build_app(
        mode=mode,
        live_ai_share=args.confirm_live_ai_share,
    )
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=args.port,
        share=share,
        inbrowser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
