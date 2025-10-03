"""Statistics and reporting for image processing."""

from typing import Dict, List, Tuple
from collections import Counter


def generate_stats_report(results: List[Dict]) -> str:
    """
    Generate a statistics report from processing results.

    Args:
        results: List of dicts with keys: theme, confidence, avg_color

    Returns:
        Formatted text report
    """
    if not results:
        return "No images processed"

    # Count by theme
    theme_counts = Counter(r['theme'] for r in results)

    # Count by confidence
    confidence_counts = Counter(r['confidence'] for r in results)

    # Calculate average RGB per theme
    theme_colors: Dict[str, List[Tuple[int, int, int]]] = {}
    for r in results:
        theme = r['theme']
        if theme not in theme_colors:
            theme_colors[theme] = []
        theme_colors[theme].append(r['avg_color'])

    theme_avg_colors = {}
    for theme, colors in theme_colors.items():
        avg_r = sum(c[0] for c in colors) // len(colors)
        avg_g = sum(c[1] for c in colors) // len(colors)
        avg_b = sum(c[2] for c in colors) // len(colors)
        theme_avg_colors[theme] = (avg_r, avg_g, avg_b)

    # Build report
    report = []
    report.append("\n" + "=" * 60)
    report.append("PROCESSING STATISTICS")
    report.append("=" * 60)
    report.append(f"\nTotal images processed: {len(results)}")

    # Theme distribution
    report.append("\n\nTHEME DISTRIBUTION")
    report.append("-" * 60)
    max_theme_len = max(len(theme) for theme in theme_counts.keys()) if theme_counts else 10

    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(results)) * 100
        bar_len = int(pct / 2)  # Scale to 50 chars max
        bar = "█" * bar_len
        avg_color = theme_avg_colors[theme]

        report.append(
            f"{theme:<{max_theme_len}} │ {count:>4} ({pct:>5.1f}%) {bar:50} "
            f"RGB({avg_color[0]:>3},{avg_color[1]:>3},{avg_color[2]:>3})"
        )

    # Confidence distribution
    report.append("\n\nCONFIDENCE LEVELS")
    report.append("-" * 60)

    for conf in ['high', 'medium', 'low']:
        count = confidence_counts[conf]
        pct = (count / len(results)) * 100 if count > 0 else 0
        bar_len = int(pct / 2)
        bar = "█" * bar_len

        conf_indicator = {
            'high': '✓',
            'medium': '~',
            'low': '?'
        }[conf]

        report.append(
            f"{conf_indicator} {conf:<8} │ {count:>4} ({pct:>5.1f}%) {bar}"
        )

    report.append("\n" + "=" * 60 + "\n")

    return "\n".join(report)


def print_simple_table(data: Dict[str, int], title: str = ""):
    """Print a simple table of key-value pairs."""
    if title:
        print(f"\n{title}")
        print("-" * len(title))

    if not data:
        print("  No data")
        return

    max_key_len = max(len(str(k)) for k in data.keys())

    for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key:<{max_key_len}} : {value}")


def format_size(bytes_count: int) -> str:
    """Format byte count to human readable."""
    if bytes_count < 1024:
        return f"{bytes_count}B"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.1f}KB"
    elif bytes_count < 1024 * 1024 * 1024:
        return f"{bytes_count / (1024 * 1024):.1f}MB"
    else:
        return f"{bytes_count / (1024 * 1024 * 1024):.1f}GB"
