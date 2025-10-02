"""Image analysis and theme detection logic."""

from PIL import Image
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

def rgb_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors."""
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)**0.5

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
    
    # Determine confidence level
    if min_dist < 30:
        confidence = 'high'
    elif min_dist < 50:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    return best_theme, min_dist, confidence

def analyze_image(path):
    """
    Full analysis of an image.
    Returns dict with color info and theme suggestion.
    """
    avg_color = get_avg_color(path)
    if not avg_color:
        return None
    
    theme, dist, confidence = detect_theme(avg_color)
    
    return {
        'avg_color': avg_color,
        'suggested_theme': theme,
        'distance': dist,
        'confidence': confidence
    }
