"""Default prompt templates for unit-distance experiments."""

UNIT_DISTANCE_GENERATION_PROMPT = """\
You are given the following mathematical problem:

Place n points in the Euclidean plane such that the number of \
unordered pairs at Euclidean distance exactly 1 is maximized.

Your task: Propose a specific finite set of planar coordinates \
(as exact rational numbers or integers) that you believe achieves \
a high unit-distance count for a given n.

Output format: A JSON array of [x, y] pairs. Example:
```json
[[0, 0], [1, 0], [0, 1]]
```

Requirements:
- All coordinates must be exact rational numbers (integers or fractions).
- No approximate decimals.
- No duplicate points.
- State how many unit-distance pairs you claim to exist.

n = {n}
"""


def format_generation_prompt(n: int) -> str:
    """Format the generation prompt for a given n."""
    return UNIT_DISTANCE_GENERATION_PROMPT.format(n=n)
