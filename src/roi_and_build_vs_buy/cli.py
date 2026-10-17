"""Unified CLI.

``roi`` runs the monthly ROI model.
``decide`` scores a build-vs-buy case and projects a 3-year TCO.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Dispatch to the ROI model or the decision kit."""

    args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="roi-and-build-vs-buy",
        description="Illustrative ROI model and build-vs-buy decision kit. No paid API on the default path.",
    )
    sub = parser.add_subparsers(dest="group", required=True)
    sub.add_parser("roi", help="monthly ROI, payback, sensitivity")
    sub.add_parser("decide", help="weighted matrix, TCO, winner stability")
    if not args or args[0] in {"-h", "--help"}:
        parser.parse_args(args)
        return 0
    if args[0] == "roi":
        from roi_and_build_vs_buy.roi.cli import main as roi_main

        return roi_main(args[1:])
    if args[0] == "decide":
        from roi_and_build_vs_buy.build_vs_buy.cli import main as decide_main

        return decide_main(args[1:])
    parser.parse_args(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
