"""
Omarchy Image Mover - Interactive theme-based image organizer
"""

__version__ = '0.0.2'
__author__ = '0xMassi'

from .main import main
from .detector import analyze_image, detect_theme
from .mover import ImageMover
from .themes import THEMES, get_theme_list

__all__ = [
    'main',
    'analyze_image',
    'detect_theme',
    'ImageMover',
    'THEMES',
    'get_theme_list',
    'Config',
    'Hisotry',
]
