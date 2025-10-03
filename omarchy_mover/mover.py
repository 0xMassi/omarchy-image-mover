"""File moving and organization operations."""

import os
import shutil
from .history import History

class ImageMover:
    """Handles moving images to theme directories."""
    
    def __init__(self, base_dir=None, history=None, dry_run=False, rename_pattern=None):
        if base_dir is None:
            home = os.path.expanduser('~')
            self.base_dir = os.path.join(home, '.local/share/omarchy/themes')
        else:
            self.base_dir = base_dir
        
        self.history = history if history else History()
        self.dry_run = dry_run
        self.rename_pattern = rename_pattern
    
    def move_image(self, img_path, theme):
        """
        Move an image to the specified theme directory.
        Returns (success, message)
        """
        target_dir = os.path.join(self.base_dir, theme, 'backgrounds')
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(img_path)
            
            # Apply rename pattern if specified
            if self.rename_pattern:
                filename = self._apply_rename_pattern(filename, self.rename_pattern)
            
            target_path = os.path.join(target_dir, filename)
            
            # Check if file already exists
            if os.path.exists(target_path):
                # Generate unique name
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    filename = f'{base}_{counter}{ext}'
                    target_path = os.path.join(target_dir, filename)
                    counter += 1
                print(f'Warning: Renamed to avoid conflict: {filename}')
            
            # Dry run mode
            if self.dry_run:
                return True, f'[DRY RUN] Would move: {filename} -> {theme}/backgrounds/'
            
            shutil.move(img_path, target_path)
            
            # Add to history
            self.history.add_entry(img_path, target_path, theme, 'move')
            
            return True, f'Moved: {filename} -> {theme}/backgrounds/'
        
        except PermissionError:
            return False, f'Error: Permission denied: {img_path}'
        except Exception as e:
            return False, f'Error moving {os.path.basename(img_path)}: {e}'
    
    def copy_image(self, img_path, theme):
        """
        Copy an image instead of moving (keeps original).
        Returns (success, message)
        """
        target_dir = os.path.join(self.base_dir, theme, 'backgrounds')
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(img_path)
            
            # Apply rename pattern if specified
            if self.rename_pattern:
                filename = self._apply_rename_pattern(filename, self.rename_pattern)
            
            target_path = os.path.join(target_dir, filename)
            
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    filename = f'{base}_{counter}{ext}'
                    target_path = os.path.join(target_dir, filename)
                    counter += 1
            
            # Dry run mode
            if self.dry_run:
                return True, f'[DRY RUN] Would copy: {filename} -> {theme}/backgrounds/'
            
            shutil.copy2(img_path, target_path)
            
            # Add to history
            self.history.add_entry(img_path, target_path, theme, 'copy')
            
            return True, f'Copied: {filename} -> {theme}/backgrounds/'
        
        except Exception as e:
            return False, f'Error copying {os.path.basename(img_path)}: {e}'
    
    def _apply_rename_pattern(self, filename, pattern):
        """Apply rename pattern to filename."""
        name, ext = os.path.splitext(filename)
        
        if '{prefix}' in pattern:
            # Pattern like: {prefix}_filename
            prefix = pattern.split('{prefix}')[0]
            return f'{prefix}{name}{ext}'
        elif '{suffix}' in pattern:
            # Pattern like: filename_{suffix}
            suffix = pattern.split('{suffix}')[1]
            return f'{name}{suffix}{ext}'
        elif '{name}' in pattern:
            # Custom pattern like: theme_{name}
            return pattern.replace('{name}', name) + ext
        
        # Default: just prepend
        return f'{pattern}{name}{ext}'
    
    def get_theme_path(self, theme):
        """Get the full path to a theme's background directory."""
        return os.path.join(self.base_dir, theme, 'backgrounds')
    
    def theme_exists(self, theme):
        """Check if a theme directory exists."""
        return os.path.isdir(os.path.join(self.base_dir, theme))
