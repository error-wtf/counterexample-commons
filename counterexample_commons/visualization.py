"""Visualization of exactly validated finite configurations."""

from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sympy import Rational  # noqa: E402


def plot_record(
    record: dict[str, Any] | None,
    show_labels: bool = True,
    show_edges: bool = True,
    show_grid: bool = True,
):
    """Create a Matplotlib plot from an exact validation record."""
    if not record:
        return None
    points = [
        (Rational(x), Rational(y))
        for x, y in record.get("points", [])
    ]
    edges = record.get("edges", [])
    fig, ax = plt.subplots(figsize=(7, 6))
    xs = [float(x) for x, _ in points]
    ys = [float(y) for _, y in points]
    ax.scatter(xs, ys, s=70, color="#1f77b4", zorder=3)
    if show_edges:
        for i, j in edges:
            ax.plot(
                [xs[i], xs[j]],
                [ys[i], ys[j]],
                color="#d62728",
                linewidth=1.8,
                zorder=2,
            )
    if show_labels:
        for index, (x, y) in enumerate(zip(xs, ys)):
            ax.annotate(
                str(index),
                (x, y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
            )
    if show_grid:
        ax.grid(True, alpha=0.25)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(record.get("configuration", "Finite configuration"))
    if points:
        pad = 0.35
        if min(xs) == max(xs):
            ax.set_xlim(min(xs) - 1, max(xs) + 1)
        else:
            ax.set_xlim(min(xs) - pad, max(xs) + pad)
        if min(ys) == max(ys):
            ax.set_ylim(min(ys) - 1, max(ys) + 1)
        else:
            ax.set_ylim(min(ys) - pad, max(ys) + pad)
    fig.tight_layout()
    return fig
