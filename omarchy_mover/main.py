#!/usr/bin/env python3
"""
Omarchy Image Mover - Interactive theme-based image organizer
"""

import argparse
import os
import sys

from .config import Config, create_default_config
from .detector import analyze_image
from .history import History
from .mover import ImageMover
from .themes import get_theme_list, is_valid_theme
from .ui import ImageBrowser, select_with_fzf, confirm


class ImageProcessor:
    """Orchestrates the image processing workflow."""
    
    def __init__(self, mode='auto', copy=False, config=None, dry_run=False, rename_pattern=None):
        self.mode = mode
        self.config = config if config else Config()
        self.history = History(
            history_file=os.path.expanduser(self.config.get('history_file')),
            max_entries=self.config.get('max_history', 100)
        )
        self.mover = ImageMover(
            base_dir=os.path.expanduser(self.config.get('base_dir')),
            history=self.history,
            dry_run=dry_run,
            rename_pattern=rename_pattern
        )
        self.copy_mode = copy
        self.dry_run = dry_run
    
    def process_images(self, images):
        """Process a batch of images."""
        if not images:
            print('No images to process.')
            return
        
        if self.dry_run:
            print('\n[DRY RUN MODE - No files will be moved]\n')
        
        print(f'\nProcessing {len(images)} image(s)...\n')
        
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for idx, img_path in enumerate(images, 1):
            print(f'[{idx}/{len(images)}] {os.path.basename(img_path)}')
            
            theme = self._select_theme_for_image(img_path)

            if not theme:
                print('   ⊘ Skipped (no theme selected)\n')
                results['skipped'] += 1
                continue
            
            # Move or copy the image
            if self.copy_mode:
                success, message = self.mover.copy_image(img_path, theme)
            else:
                success, message = self.mover.move_image(img_path, theme)
            
            print(f'   {message}\n')
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
        
        # Summary
        print('=' * 50)
        print(f'Success: {results["success"]}')
        if results['failed']:
            print(f'Failed: {results["failed"]}')
        if results['skipped']:
            print(f'Skipped: {results["skipped"]}')
        print('=' * 50)

        # Show undo hint if images were moved
        if not self.dry_run and results['success'] > 0:
            print('\n💡 To undo this operation, run: oim --undo')
    
    def _select_theme_for_image(self, img_path):
        """Select theme for a single image based on mode."""
        if self.mode == 'manual':
            return self._manual_theme_selection(img_path)
        else:
            return self._auto_theme_selection(img_path)
    
    def _auto_theme_selection(self, img_path):
        """Auto-detect theme with fallback to manual selection."""
        analysis = analyze_image(img_path)

        if not analysis:
            print('   Warning: Could not analyze image')
            return self._manual_theme_selection(img_path)

        theme = analysis['suggested_theme']
        confidence = analysis['confidence']
        distance = analysis['distance']
        rgb = analysis['avg_color']

        # Show detection result
        confidence_symbols = {'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}
        symbol = confidence_symbols.get(confidence, '[?]')

        print(f'   {symbol} Detected: {theme} (RGB: {rgb}, distance: {distance:.1f})')

        # Always ask for confirmation in auto mode
        # Include filename in prompt so user knows which image they're confirming
        filename = os.path.basename(img_path)
        try:
            confirmed = confirm(
                f'   [{filename}] Use theme "{theme}"?',
                yes_text='Yes, use this theme',
                no_text='No, pick different theme'
            )
            if not confirmed:
                print('   ↻ Opening manual theme selection...')
                return self._manual_theme_selection(img_path)
        except KeyboardInterrupt:
            print('\n   Cancelled by user')
            return None

        return theme
    
    def _manual_theme_selection(self, img_path):
        """Let user manually select theme."""
        try:
            themes = get_theme_list()
            theme = select_with_fzf(themes, '   Select theme: ')

            if theme and is_valid_theme(theme):
                return theme
            return None
        except KeyboardInterrupt:
            print('\n   Cancelled by user')
            return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Omarchy Image Mover - Sort images into theme directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  oim                              # Start in home directory
  oim ~/Pictures                   # Start in specific directory
  oim --auto                       # Auto-detect themes
  oim --manual                     # Manually select themes
  oim --copy                       # Copy instead of move
  oim --dry-run                    # Preview without moving
  oim --rename "wallpaper_{name}"  # Rename with pattern
  oim --undo                       # Undo last operation
  oim --history                    # Show recent operations
  oim --config                     # Create default config file
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='~',
        help='Starting directory or image file (default: home directory)'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect themes based on image colors'
    )
    
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Manually select theme for each image'
    )
    
    parser.add_argument(
        '--copy',
        action='store_true',
        help='Copy images instead of moving them'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually moving files'
    )
    
    parser.add_argument(
        '--rename',
        metavar='PATTERN',
        help='Rename pattern (use {name}, {prefix}, {suffix})'
    )
    
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Undo the last operation'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show recent operations'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Create default config file'
    )
    
    parser.add_argument(
        '--config-path',
        metavar='PATH',
        help='Path to config file'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = Config(args.config_path) if args.config_path else Config()
    history = History(
        history_file=os.path.expanduser(config.get('history_file')),
        max_entries=config.get('max_history', 100)
    )
    
    # Handle special commands
    if args.config:
        config_path = create_default_config()
        print(f'\nEdit this file to customize themes and settings.')
        sys.exit(0)
    
    if args.undo:
        success, msg = history.undo_last()
        print(msg)
        sys.exit(0 if success else 1)
    
    if args.history:
        recent = history.get_recent(20)
        if not recent:
            print('No recent operations.')
        else:
            print('\nRecent operations:')
            print('=' * 60)
            for i, entry in enumerate(reversed(recent), 1):
                print(f'{i}. {history.format_entry(entry)}')
            print('=' * 60)
            print(f'\nTo undo: oim --undo')
        sys.exit(0)
    
    # Determine mode
    if args.auto and args.manual:
        print('Error: Cannot use both --auto and --manual')
        sys.exit(1)
    
    # Collect images
    start_path = os.path.expanduser(args.path)
    images = []
    
    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
    
    try:
        if os.path.isfile(start_path) and start_path.lower().endswith(IMAGE_EXTS):
            # Single image provided
            images = [start_path]
            mode = 'auto' if args.auto else 'manual' if args.manual else select_with_fzf(
                ['auto', 'manual'], 'Mode: '
            )
        else:
            # Directory browsing
            if not os.path.isdir(start_path):
                print(f'Error: Invalid path: {start_path}')
                sys.exit(1)

            # Select mode first if not specified
            if not args.auto and not args.manual:
                mode = select_with_fzf(['auto', 'manual'], 'Processing mode: ')
                if not mode:
                    print('Error: No mode selected')
                    sys.exit(0)
            else:
                mode = 'auto' if args.auto else 'manual'

            print(f'\nBrowse and select images (ESC when done)\n')

            browser = ImageBrowser(start_path)
            images = browser.run()
    except KeyboardInterrupt:
        print('\n\nCancelled by user.')
        sys.exit(0)
    
    if not images:
        print('\nNo images selected. Goodbye!')
        sys.exit(0)
    
    # Process images
    processor = ImageProcessor(
        mode=mode,
        copy=args.copy,
        config=config,
        dry_run=args.dry_run,
        rename_pattern=args.rename
    )

    try:
        processor.process_images(images)
        print('\nDone!')
    except KeyboardInterrupt:
        print('\n\nOperation cancelled by user. No files were moved.')
        sys.exit(0)


if __name__ == '__main__':
    main()
