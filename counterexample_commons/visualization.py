"""Matplotlib visualization for exactly validated configurations."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def plot_configuration(
    points,
    edges=None,
    title="Validated Configuration",
    boundary_note=None,
    show_labels=True,
    show_edges=True,
    show_grid=True,
):
    """Plot points and already-validated unit-distance edges.

    This function intentionally contains no edge-finding logic. The edges
    parameter must come from the exact validation path.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    dense = len(points) > 50 or (edges is not None and len(edges) > 50)
    ax.scatter(
        xs,
        ys,
        s=42 if dense else 90,
        c="#2f55ff",
        edgecolors="#2440bd",
        linewidths=0.6 if dense else 1.0,
        zorder=5,
    )
    if show_edges and edges:
        edge_lw = 0.65 if dense else 1.4
        edge_alpha = 0.42 if dense else 0.75
        for i, j in edges:
            ax.plot(
                [points[i][0], points[j][0]],
                [points[i][1], points[j][1]],
                color="#ff6b6b",
                lw=edge_lw,
                alpha=edge_alpha,
                zorder=2,
            )
    if show_labels:
        for i, (x, y) in enumerate(points):
            ax.annotate(
                str(i),
                (x, y),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=6 if dense else 8,
            )
    ax.set_aspect("equal", adjustable="box")
    if show_grid:
        ax.grid(True, alpha=0.25, linestyle="--")
    else:
        ax.grid(False)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if xs and ys:
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)
        x_pad = max(0.2, x_span * 0.08)
        y_pad = max(0.2, y_span * 0.08)
        ax.set_xlim(min(xs) - x_pad, max(xs) + x_pad)
        ax.set_ylim(min(ys) - y_pad, max(ys) + y_pad)
    full_title = title + (f"\n{boundary_note}" if boundary_note else "")
    ax.set_title(full_title, fontsize=10)
    plt.tight_layout()
    return fig


def plot_title_for_result(result) -> str:
    """Return a concise plot title; long boundaries stay in UI markdown."""
    if result.name == "Finite Rational Mesh Baseline":
        return (
            f"{result.name} - {result.point_count} points, "
            f"{result.edge_count} exact edges"
        )
    return result.name


def plot_from_result(
    result,
    show_labels=True,
    show_edges=True,
    show_grid=True,
):
    """Plot from ValidatedConfigurationResult."""
    points, edges = result.to_plot_data()
    return plot_configuration(
        points,
        edges,
        plot_title_for_result(result),
        None,
        show_labels=show_labels,
        show_edges=show_edges,
        show_grid=show_grid,
    )
