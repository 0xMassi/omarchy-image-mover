"""Theme definitions and color data for Omarchy image sorter."""

# Predefined themes with background RGB values
THEMES = {
    'catppuccin': (30, 30, 46),
    'catppuccin-latte': (239, 241, 245),
    'everforest': (43, 51, 57),
    'gruvbox': (40, 40, 40),
    'kanagawa': (31, 31, 40),
    'matte-black': (40, 40, 43),
    'nord': (46, 52, 64),
    'osaka-jade': (0, 168, 107),
    'ristretto': (31, 14, 4),
    'rose-pine': (25, 23, 36),
    'tokyo-night': (26, 27, 38),
}

def get_theme_list():
    """Return sorted list of theme names."""
    return sorted(THEMES.keys())

def get_theme_color(theme_name):
    """Get RGB color for a theme."""
    return THEMES.get(theme_name)

def is_valid_theme(theme_name):
    """Check if theme exists."""
    return theme_name in THEMES
