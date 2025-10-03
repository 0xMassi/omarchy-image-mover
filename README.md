# Omarchy Image Mover

Interactive theme-based image organizer designed for the Omarchy distribution. Intelligently sorts wallpapers into theme directories using automatic color detection.

**Note**: This tool is specifically designed for the Omarchy distribution running on ARM devices.

## Features

- **Improved Auto-detection**: Uses dominant color analysis with perceptual color weighting for accurate theme matching
- **Live Preview**: See detected theme directly in the image preview pane before selection
- **Visual Selection Indicators**: Checkmark (✓) shows already-selected images during browsing
- **Interactive browsing**: Navigate directories with persistent selection
- **Batch processing**: Select multiple images with clear filename identification in prompts
- **Confidence scoring**: Get feedback on detection accuracy (HIGH/MED/LOW)
- **User Confirmation**: Always prompts before moving files - no automatic operations
- **Flexible workflow**: Continue selecting or process at any time
- **Smart navigation**: DONE/CLEAR options for easy workflow control
- **Copy mode**: Preserve originals while organizing
- **Keyboard Interrupt Handling**: Press Ctrl+C at any time to safely cancel without moving files

## Requirements

- Omarchy distribution (ARM devices)
- Python 3.8+
- [fzf](https://github.com/junegunn/fzf) - fuzzy finder
- Pillow (installed automatically)

### Install fzf

```bash
# On Omarchy/Arch-based ARM
sudo pacman -S fzf
```

## Installation

```bash
# Clone the repository
git clone https://github.com/0xMassi/omarchy-image-mover.git
cd omarchy-image-mover

# Install in development mode
pip install -e .

# Or install from PyPI (coming soon)
pip install omarchy-image-mover
```

## Quick Start

```bash
# Start in current directory
oim

# Start in specific directory
oim ~/Pictures

# Process single image with auto-detection
oim --auto wallpaper.png
```

## Usage

### Basic Commands

All commands are equivalent:
- `oim` (recommended - short and easy)
- `omarchy-mover` (full name)

```bash
# Browse and select images interactively
oim ~/Downloads

# Auto-detect themes for all images
oim --auto ~/Pictures

# Manually select themes
oim --manual ~/Pictures

# Copy instead of move (keeps originals)
oim --copy ~/Pictures

# Process a single image
oim path/to/image.png
```

### Interactive Mode Workflow

1. **Navigate** with arrow keys or j/k
2. **Preview** images - theme detection shown in preview pane
3. **Select images** with Tab (multi-select) - selected images show ✓ checkmark
4. **Continue selecting** or navigate to `[DONE]` when ready
5. **Press Enter** on `[DONE]` to process
6. **Review** each image with detected theme and filename
7. **Confirm** - Choose "Yes, use this theme" or "No, pick different theme"
8. **Complete** - View summary and optional undo command

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Arrow keys / j/k | Navigate entries |
| Enter | Confirm selection / Enter directory / Process when on [DONE] |
| Tab | Toggle image selection |
| Ctrl+A | Select all |
| Ctrl+D | Deselect all |
| Ctrl+C | Cancel operation safely (no files moved) |
| ESC | Action menu / Cancel |

### Selection Indicators

When browsing, you'll see:
- `[DIR] folder/` - Directory
- `[IMG] image.png (2.3MB)` - Image file with size
- `[IMG] ✓ selected.png (1.8MB)` - Already selected image (checkmark)
- `[UP] ../` - Parent directory
- `[DONE] Process X image(s)` - Appears when images are selected
- `[CLEAR] Clear selection` - Remove all selections

### Preview Pane

When you hover over an image, the preview pane shows:
```
File: wallpaper.png
1920x1080 | JPEG | 2.3MB
Theme: [HIGH] catppuccin-latte (dist: 0.9)

[Image preview]
```

This lets you see what theme will be suggested before you even select the file.

## Supported Themes

- **catppuccin** - Mocha dark theme
- **catppuccin-latte** - Light variant
- **everforest** - Forest green dark theme
- **gruvbox** - Retro warm theme
- **kanagawa** - Japanese-inspired theme
- **matte-black** - Pure dark theme
- **nord** - Arctic blue theme
- **osaka-jade** - Vibrant green accent
- **ristretto** - Coffee brown theme
- **rose-pine** - Muted purple theme
- **tokyo-night** - Neon dark theme

## Output Structure

Images are organized in:

```
~/.local/share/omarchy/themes/
├── catppuccin/
│   └── backgrounds/
│       ├── sunset.png
│       └── mountains.jpg
├── gruvbox/
│   └── backgrounds/
│       └── forest.png
└── ...
```

## Examples

### Example 1: Quick Sort Downloads

```bash
oim ~/Downloads
# Browse images - see theme preview in right pane
# Tab to select multiple images (✓ checkmark appears)
# Navigate to [DONE] and press Enter
# For each image, you'll see:
#   [HIGH] Detected: catppuccin (RGB: (30, 30, 46), distance: 12.3)
#   [filename.jpg] Use theme "catppuccin"?
#     > Yes, use this theme
#       No, pick different theme
# View summary at the end
```

### Example 2: Process Single Image

```bash
oim --auto ~/Pictures/dark-forest.png
# Output:
# [1/1] dark-forest.png
#    [HIGH] Detected: everforest (RGB: (43, 51, 57), distance: 8.2)
#    [dark-forest.png] Use theme "everforest"?
#      > Yes, use this theme
#    ✓ Moved: dark-forest.png → everforest/backgrounds/
#
# 💡 To undo this operation, run: oim --undo
```

### Example 3: Manual Theme Selection

```bash
oim --manual vacation-photos/
# Browse and select multiple images
# Manually choose theme for each
# Images sorted to chosen themes
```

### Example 4: Copy Mode (Preserve Originals)

```bash
oim --copy --auto ~/wallpapers
# Creates copies in theme folders
# Original files remain untouched
```

## Confidence Levels

Auto-detection provides confidence feedback based on perceptual color distance:

- **[HIGH]** (distance < 20): Very confident match - colors are very similar
- **[MED]** (distance < 35): Good match - colors are reasonably close
- **[LOW]** (distance ≥ 35): Uncertain match - colors differ significantly

All detections require user confirmation before moving files. You can choose to accept the suggestion or pick a different theme manually.

## Troubleshooting

### Command not found: oim

After installation, make sure your Python bin directory is in PATH:

```bash
# Check where it's installed
pip show omarchy-image-mover

# Add to PATH (Linux/Mac) - add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

### fzf not found

Install fzf on Omarchy:

```bash
sudo pacman -S fzf
```

### Permission denied

Ensure write permissions to the themes directory:

```bash
mkdir -p ~/.local/share/omarchy/themes
chmod 755 ~/.local/share/omarchy/themes
```

### Images not detected

Supported formats:
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- WebP (`.webp`)
- BMP (`.bmp`)

### Changes not taking effect

After modifying `setup.py`, reinstall:

```bash
pip uninstall omarchy-image-mover -y
pip install -e .
```

## Development

### Running from source

```bash
python -m omarchy_mover.main
```

### Project structure

```
omarchy-image-mover/
├── omarchy_mover/
│   ├── __init__.py    # Package initialization
│   ├── main.py        # Entry point and orchestration
│   ├── ui.py          # FZF interface and navigation
│   ├── detector.py    # Color analysis and theme detection
│   ├── mover.py       # File operations
│   └── themes.py      # Theme definitions
├── setup.py           # Package configuration
└── README.md
```

### Adding new themes

Edit `omarchy_mover/themes.py`:

```python
THEMES = {
    'my-custom-theme': (R, G, B),  # Add your theme RGB values
    # ...
}
```

Then reinstall: `pip install -e .`

### Running tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest

# Code formatting
black omarchy_mover/

# Linting
flake8 omarchy_mover/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for contributions

- Add more themes
- Improve color detection algorithm
- Add image preview in fzf
- Config file support
- Undo/redo functionality
- Better test coverage

## License

MIT License - see LICENSE file for details.

## Author

Created by [0xMassi](https://github.com/0xMassi)

## Screenshots

### Interactive Browser
<!-- Screenshot of the fzf interactive browser showing image selection -->

### Theme Detection
<!-- Screenshot showing the auto-detection results with confidence scores -->

### Theme Selection
<!-- Screenshot of manual theme selection interface -->

### Processing Results
<!-- Screenshot showing successful image organization -->

## Acknowledgments

- Built for Omarchy theme management
- Uses [fzf](https://github.com/junegunn/fzf) for fuzzy finding
- Inspired by the need for efficient wallpaper organization

## Support

- Issues: [GitHub Issues](https://github.com/0xMassi/omarchy-image-mover/issues)
- Discussions: [GitHub Discussions](https://github.com/0xMassi/omarchy-image-mover/discussions)
