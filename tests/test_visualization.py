"""Tests for visualization module."""
import inspect

from counterexample_commons import visualization
from counterexample_commons.visualization import (
    plot_configuration,
    plot_from_result,
)
from counterexample_commons.validated_result import (
    ValidatedConfigurationResult,
)


class TestVisualization:
    """Test matplotlib visualization functions."""

    def test_plot_configuration_returns_figure(self):
        """plot_configuration returns a matplotlib figure."""
        points = [(0, 0), (1, 0), (0.6, 0.8)]
        edges = [(0, 1), (0, 2)]
        fig = plot_configuration(points, edges, "Test", "Boundary note")
        assert fig is not None
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_plot_configuration_no_edges(self):
        """plot_configuration works without edges."""
        points = [(0, 0), (1, 0)]
        fig = plot_configuration(points, None, "Test", None)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_plot_from_result(self):
        """plot_from_result uses ValidatedConfigurationResult."""
        result = ValidatedConfigurationResult(
            name="Test Config",
            points=[("0", "0"), ("1", "0")],
            exact_edges=[(0, 1)],
            edge_count=1,
            validation_status="LOCALLY_REPRODUCED_EXACT",
            scientific_scope="Test scope",
            source_kind="TEST",
        )
        fig = plot_from_result(result)
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_plot_configuration_has_correct_title(self):
        """Figure title includes name and boundary note."""
        points = [(0, 0), (1, 0)]
        fig = plot_configuration(points, [(0, 1)], "Line", "Finite baseline")
        assert fig.axes[0].get_title() == "Line\nFinite baseline"
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_visualization_has_no_edge_finding_logic(self):
        """Visualization draws validated edges; it does not decide them."""
        source = inspect.getsource(visualization)
        assert "count_unit_edges" not in source
        assert "squared_distance" not in source
        assert "== 1" not in source

    def test_show_edges_false_draws_no_edge_lines(self):
        """Edge visibility control must not change validated point data."""
        points = [(0, 0), (1, 0)]
        fig = plot_configuration(
            points,
            [(0, 1)],
            "Line",
            "Finite baseline",
            show_edges=False,
        )
        assert len(fig.axes[0].lines) == 0
        import matplotlib.pyplot as plt
        plt.close(fig)
