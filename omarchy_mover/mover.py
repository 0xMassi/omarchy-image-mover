"""File moving and organization operations."""

import os
import shutil

class ImageMover:
    """Handles moving images to theme directories."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            home = os.path.expanduser('~')
            self.base_dir = os.path.join(home, '.local/share/omarchy/themes')
        else:
            self.base_dir = base_dir
    
    def move_image(self, img_path, theme):
        """
        Move an image to the specified theme directory.
        Returns (success, message)
        """
        target_dir = os.path.join(self.base_dir, theme, 'backgrounds')
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(img_path)
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
                print(f'⚠️  Renamed to avoid conflict: {filename}')
            
            shutil.move(img_path, target_path)
            return True, f'✓ {filename} → {theme}/backgrounds/'
        
        except PermissionError:
            return False, f'✗ Permission denied: {img_path}'
        except Exception as e:
            return False, f'✗ Error moving {os.path.basename(img_path)}: {e}'
    
    def copy_image(self, img_path, theme):
        """
        Copy an image instead of moving (keeps original).
        Returns (success, message)
        """
        target_dir = os.path.join(self.base_dir, theme, 'backgrounds')
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(img_path)
            target_path = os.path.join(target_dir, filename)
            
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    filename = f'{base}_{counter}{ext}'
                    target_path = os.path.join(target_dir, filename)
                    counter += 1
            
            shutil.copy2(img_path, target_path)
            return True, f'✓ {filename} → {theme}/backgrounds/ (copied)'
        
        except Exception as e:
            return False, f'✗ Error copying {os.path.basename(img_path)}: {e}'
    
    def get_theme_path(self, theme):
        """Get the full path to a theme's background directory."""
        return os.path.join(self.base_dir, theme, 'backgrounds')
    
    def theme_exists(self, theme):
        """Check if a theme directory exists."""
        return os.path.isdir(os.path.join(self.base_dir, theme))
