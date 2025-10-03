"""Image analysis and theme detection logic."""

from PIL import Image
from collections import Counter
from .themes import THEMES

def get_avg_color(path):
    """Calculate average RGB color of an image."""
    try:
        with Image.open(path) as img:
            img = img.convert('RGB')
            pixels = list(img.getdata())
            if not pixels:
                return None
            r, g, b = zip(*pixels)
            return (sum(r) // len(r), sum(g) // len(g), sum(b) // len(b))
    except Exception as e:
        print(f'⚠️  Error reading {path}: {e}')
        return None

def get_dominant_color(path):
    """
    Get dominant color using color quantization.
    More accurate than simple average for theme detection.
    """
    try:
        with Image.open(path) as img:
            # Resize for faster processing
            img = img.convert('RGB')
            img.thumbnail((200, 200))

            # Get color palette - reduce to most common colors
            pixels = list(img.getdata())

            # Quantize colors to reduce noise (group similar colors)
            quantized = []
            for r, g, b in pixels:
                # Round to nearest 16 to group similar colors
                qr = (r // 16) * 16
                qg = (g // 16) * 16
                qb = (b // 16) * 16
                quantized.append((qr, qg, qb))

            # Find most common color
            color_counts = Counter(quantized)
            dominant = color_counts.most_common(1)[0][0]

            return dominant
    except Exception as e:
        print(f'⚠️  Error reading {path}: {e}')
        return None

def rgb_distance(c1, c2):
    """
    Calculate weighted Euclidean distance between two RGB colors.
    Uses perceptual weighting to better match human color perception.
    """
    # Weight red less, green more (closer to human perception)
    r_weight = 0.3
    g_weight = 0.59
    b_weight = 0.11

    r_diff = (c1[0] - c2[0]) * r_weight
    g_diff = (c1[1] - c2[1]) * g_weight
    b_diff = (c1[2] - c2[2]) * b_weight

    return (r_diff**2 + g_diff**2 + b_diff**2)**0.5

def detect_theme(avg_color):
    """
    Detect the best matching theme for a color.
    Returns (theme_name, distance, confidence_level)
    """
    min_dist = float('inf')
    best_theme = None

    for theme, color in THEMES.items():
        dist = rgb_distance(avg_color, color)
        if dist < min_dist:
            min_dist = dist
            best_theme = theme

    # Determine confidence level with adjusted thresholds for weighted distance
    if min_dist < 20:
        confidence = 'high'
    elif min_dist < 35:
        confidence = 'medium'
    else:
        confidence = 'low'

    return best_theme, min_dist, confidence

def analyze_image(path):
    """
    Full analysis of an image.
    Returns dict with color info and theme suggestion.
    Uses dominant color detection for better accuracy.
    """
    # Try dominant color first (more accurate)
    dominant_color = get_dominant_color(path)
    if not dominant_color:
        # Fallback to average if dominant fails
        dominant_color = get_avg_color(path)
        if not dominant_color:
            return None

    theme, dist, confidence = detect_theme(dominant_color)

    return {
        'avg_color': dominant_color,
        'suggested_theme': theme,
        'distance': dist,
        'confidence': confidence
    }
