#!/usr/bin/env python3
"""
Omarchy Image Mover - Interactive theme-based image organizer
"""

import argparse
import os
import sys

from .detector import analyze_image
from .mover import ImageMover
from .themes import get_theme_list, is_valid_theme
from .ui import ImageBrowser, select_with_fzf, confirm


class ImageProcessor:
    """Orchestrates the image processing workflow."""
    
    def __init__(self, mode='auto', copy=False):
        self.mode = mode
        self.mover = ImageMover()
        self.copy_mode = copy
    
    def process_images(self, images):
        """Process a batch of images."""
        if not images:
            print('📭 No images to process.')
            return
        
        print(f'\n📦 Processing {len(images)} image(s)...\n')
        
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for idx, img_path in enumerate(images, 1):
            print(f'[{idx}/{len(images)}] {os.path.basename(img_path)}')
            
            theme = self._select_theme_for_image(img_path)
            
            if not theme:
                print('   ⏭️  Skipped\n')
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
        print(f'✅ Success: {results["success"]}')
        if results['failed']:
            print(f'❌ Failed: {results["failed"]}')
        if results['skipped']:
            print(f'⏭️  Skipped: {results["skipped"]}')
        print('=' * 50)
    
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
            print('   ⚠️  Could not analyze image')
            return self._manual_theme_selection(img_path)
        
        theme = analysis['suggested_theme']
        confidence = analysis['confidence']
        distance = analysis['distance']
        rgb = analysis['avg_color']
        
        # Show detection result
        confidence_emoji = {'high': '🎯', 'medium': '🤔', 'low': '❓'}
        emoji = confidence_emoji.get(confidence, '❓')
        
        print(f'   {emoji} Detected: {theme} (confidence: {confidence}, RGB: {rgb})')
        
        # Ask for confirmation if low confidence
        if confidence == 'low':
            if not confirm(f'   Low confidence ({distance:.1f}). Use this theme?'):
                return self._manual_theme_selection(img_path)
        
        return theme
    
    def _manual_theme_selection(self, img_path):
        """Let user manually select theme."""
        themes = get_theme_list()
        theme = select_with_fzf(themes, '   Select theme: ')
        
        if theme and is_valid_theme(theme):
            return theme
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Omarchy Image Mover - Sort images into theme directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omarchy-mover                    # Start in home directory
  omarchy-mover ~/Pictures         # Start in specific directory
  omarchy-mover --auto             # Auto-detect themes
  omarchy-mover --manual           # Manually select themes
  omarchy-mover --copy             # Copy instead of move
  omarchy-mover image.png          # Process single image
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
    
    args = parser.parse_args()
    
    # Determine mode
    if args.auto and args.manual:
        print('❌ Cannot use both --auto and --manual')
        sys.exit(1)
    
    # Collect images
    start_path = os.path.expanduser(args.path)
    images = []
    
    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
    
    if os.path.isfile(start_path) and start_path.lower().endswith(IMAGE_EXTS):
        # Single image provided
        images = [start_path]
        mode = 'auto' if args.auto else 'manual' if args.manual else select_with_fzf(
            ['auto', 'manual'], 'Mode: '
        )
    else:
        # Directory browsing
        if not os.path.isdir(start_path):
            print(f'❌ Invalid path: {start_path}')
            sys.exit(1)
        
        # Select mode first if not specified
        if not args.auto and not args.manual:
            mode = select_with_fzf(['auto', 'manual'], 'Processing mode: ')
            if not mode:
                print('❌ No mode selected')
                sys.exit(0)
        else:
            mode = 'auto' if args.auto else 'manual'
        
        print(f'\n🔍 Browse and select images (ESC when done)\n')
        
        browser = ImageBrowser(start_path)
        images = browser.run()
    
    if not images:
        print('\n👋 No images selected. Goodbye!')
        sys.exit(0)
    
    # Process images
    processor = ImageProcessor(mode=mode, copy=args.copy)
    processor.process_images(images)
    
    print('\n✨ Done!')


if __name__ == '__main__':
    main()
