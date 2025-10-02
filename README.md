# Omarchy Image Mover

Interactive theme-based image organizer that intelligently sorts wallpapers into theme directories using automatic color detection.

## Features

- **Auto-detection**: Analyzes image colors and suggests matching themes
- **Interactive browsing**: Navigate directories with persistent selection
- **Batch processing**: Select multiple images before processing
- **Confidence scoring**: Get feedback on detection accuracy
- **Flexible workflow**: Continue selecting or process at any time
- **Smart navigation**: DONE/CLEAR options for easy workflow control
- **Copy mode**: Preserve originals while organizing

## Requirements

- Python 3.8+
- [fzf](https://github.com/junegunn/fzf) - fuzzy finder
- Pillow (installed automatically)

### Install fzf

```bash
# Arch Linux
sudo pacman -S fzf

# Debian/Ubuntu/Armbian
sudo apt install fzf

# macOS
brew install fzf
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

All three commands are equivalent:
- `oim` (recommended - short and easy)
- `omi` (alternative short form)
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
2. **Select images** with Tab (multi-select)
3. **Continue selecting** or navigate to `[DONE]` when ready
4. **Press Enter** on `[DONE]` to process
5. **Review** auto-detected themes and confirm/override

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Arrow keys / j/k | Navigate entries |
| Enter | Confirm selection / Enter directory / Process when on [DONE] |
| Tab | Toggle image selection |
| Ctrl+A | Select all |
| Ctrl+D | Deselect all |
| ESC | Action menu / Cancel |

### Selection Indicators

When browsing, you'll see:
- `[DIR] folder/` - Directory
- `[IMG] image.png` - Image file
- `[UP] ../` - Parent directory
- `[DONE] Process X image(s)` - Appears when images are selected
- `[CLEAR] Clear selection` - Remove all selections

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
# Tab through images to select
# Navigate to [DONE] and press Enter
# Review auto-detected themes
# Confirm or manually override
```

### Example 2: Process Single Image

```bash
oim --auto ~/Pictures/dark-forest.png
# Output:
# [1/1] dark-forest.png
#    Detected: everforest (confidence: high, RGB: (43, 51, 57))
#    ✓ dark-forest.png → everforest/backgrounds/
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

Auto-detection provides confidence feedback:

- **High** (distance < 30): Very confident match
- **Medium** (distance < 50): Good match, usually correct
- **Low** (distance > 50): Uncertain, manual confirmation recommended

Low confidence detections will prompt for confirmation before proceeding.

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

Install fzf using your package manager:

```bash
# Arch/Manjaro
sudo pacman -S fzf

# Debian/Ubuntu
sudo apt install fzf

# Fedora
sudo dnf install fzf

# macOS
brew install fzf
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

## Acknowledgments

- Built for [Omarchy](https://github.com/yourusername/omarchy) theme management
- Uses [fzf](https://github.com/junegunn/fzf) for fuzzy finding
- Inspired by the need for efficient wallpaper organization

## Support

- Issues: [GitHub Issues](https://github.com/0xMassi/omarchy-image-mover/issues)
- Discussions: [GitHub Discussions](https://github.com/0xMassi/omarchy-image-mover/discussions)
