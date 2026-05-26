'''Visualization of exactly validated point configurations.'''

import io
import base64
from typing import Sequence, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sympy import Rational


def plot_validated_configuration(
    points: Sequence[tuple[Rational, Rational]],
    edges: Sequence[tuple[int, int]],
    title: str = '',
    scope_text: str = '',
    show_labels: bool = True,
    show_edges: bool = True,
    show_grid: bool = True,
) -> Optional[str]:
    '''Plot points and exactly validated edges.
    
    Returns base64-encoded PNG data URL.
    '''
    if not points:
        return None
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    
    ax.scatter(xs, ys, s=150, c='blue', zorder=3, edgecolors='white', linewidths=2)
    
    if show_labels:
        for i, (x, y) in enumerate(zip(xs, ys)):
            ax.annotate(str(i), (x, y), textcoords='offset points',
                       xytext=(5, 5), fontsize=9, fontweight='bold')
    
    if show_edges and edges:
        for i, j in edges:
            if 0 <= i < len(points) and 0 <= j < len(points):
                ax.plot([xs[i], xs[j]], [ys[i], ys[j]],
                       'r-', linewidth=2, zorder=2, alpha=0.7)
    
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='--')
    
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    
    ax.set_title(title or 'Validated Configuration', fontsize=14, fontweight='bold')
    
    if xs and ys:
        margin = 0.5
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin, max(ys) + margin)
    
    if scope_text:
        fig.text(0.5, 0.02, scope_text, ha='center', fontsize=9,
                style='italic', color='gray')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    
    return f'data:image/png;base64,{img_data}'


def format_summary(
    configuration: str,
    n_points: int,
    n_edges: int,
    validation_status: str,
    scientific_scope: str,
) -> str:
    '''Format markdown summary for visualization.'''
    return f'''### Configuration Summary

| Property | Value |
|----------|-------|
| **Configuration** | {configuration} |
| **Number of points** | {n_points} |
| **Exactly validated unit-distance edges** | {n_edges} |
| **Validation status** | {validation_status} |
| **Scientific scope** | {scientific_scope} |
'''
