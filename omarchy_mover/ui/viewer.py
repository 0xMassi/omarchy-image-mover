"""Interactive image viewer with rotation and rename."""

import os
import subprocess
import sys
import time
from PIL import Image
from .preview import has_preview_support

class ImageViewer:
    """Interactive image viewer with live preview and editing."""
    
    def __init__(self):
        self.tool = has_preview_support()
        if not self.tool:
            print("Warning: No image preview tool found")
            print("Install chafa: sudo pacman -S chafa")
    
    def view_and_edit(self, image_path):
        """View image with live preview and editing options."""
        if not self.tool:
            return self._simple_edit(image_path)
        
        return self._terminal_viewer(image_path)
    
    def _clear_screen(self):
        """Clear terminal screen."""
        subprocess.run(['clear'], check=False)
    
    def _show_image(self, image_path):
        """Display image in terminal with best quality."""
        try:
            # Get terminal size
            result = subprocess.run(['stty', 'size'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                rows, cols = result.stdout.strip().split()
                width = int(cols)
                height = int(rows) - 8  # Leave space for controls
            else:
                width, height = 120, 35
        except:
            width, height = 120, 35
        
        if self.tool == 'chafa':
            subprocess.run([
                'chafa',
                f'--size={width}x{height}',
                '--format=symbols',
                '--symbols=vhalf,wedge',
                '--colors=full',
                '--dither=diffusion',
                image_path
            ], stderr=subprocess.DEVNULL, check=False)
        
        elif self.tool == 'viu':
            subprocess.run(['viu', '-t', image_path], stderr=subprocess.DEVNULL, check=False)
        
        elif self.tool == 'kitty':
            subprocess.run([
                'kitty', '+kitten', 'icat',
                '--clear',
                '--transfer-mode=memory',
                '--stdin=no',
                image_path
            ], stderr=subprocess.DEVNULL, check=False)
    
    def _get_image_info(self, image_path):
        """Get image information."""
        try:
            with Image.open(image_path) as img:
                return {
                    'size': img.size,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception:
            return None
    
    def _terminal_viewer(self, image_path):
        """Terminal-based viewer with keyboard controls."""
        modified = False
        current_path = image_path
        
        while True:
            self._clear_screen()
            
            # Show image
            self._show_image(current_path)
            
            # Show minimal info bar
            info = self._get_image_info(current_path)
            filename = os.path.basename(current_path)
            
            print(f"\nFile: {filename}", end="")
            if info:
                print(f" | {info['size'][0]}x{info['size'][1]} | {info['format']}", end="")
            print()
            
            # Show clean controls
            print("\nR:Rotate Right  L:Rotate Left  N:Rename  Q:Done/Next")
            print("Action: ", end="", flush=True)
            
            # Get single keypress - use stdin redirect to work in subprocess context
            try:
                # Open /dev/tty to read from terminal directly
                result = subprocess.run(
                    ['bash', '-c', 'read -n 1 -s -r key < /dev/tty; echo "$key"'],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False
                )
                key = result.stdout.strip().lower()

                if not key or key == 'q':
                    break
                elif key == 'r':
                    current_path = self._rotate_image(current_path, 'right')
                    if current_path:
                        modified = True
                elif key == 'l':
                    current_path = self._rotate_image(current_path, 'left')
                    if current_path:
                        modified = True
                elif key == 'n':
                    new_path = self._rename_image(current_path)
                    if new_path:
                        current_path = new_path
                        modified = True
                else:
                    # Show message for invalid key
                    print(f"\nInvalid key: '{key}'. Press R, L, N, or Q", end="", flush=True)
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\nCancelled")
                break
            except subprocess.TimeoutExpired:
                print("\nTimeout - no input received")
                break
            except Exception as e:
                print(f"\nError reading input: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(2)
                break
        
        return modified, current_path
    
    def _rotate_image(self, image_path, direction):
        """Rotate image and save."""
        try:
            with Image.open(image_path) as img:
                if direction == 'right':
                    rotated = img.rotate(-90, expand=True)
                else:
                    rotated = img.rotate(90, expand=True)
                
                rotated.save(image_path)
                return image_path
        except Exception as e:
            print(f"\nError rotating: {e}")
            time.sleep(1)
            return image_path
    
    def _rename_image(self, image_path):
        """Rename image file."""
        old_name = os.path.basename(image_path)
        dir_path = os.path.dirname(image_path)
        
        self._clear_screen()
        print(f"Current: {old_name}\n")
        
        try:
            # Use /dev/tty for input
            result = subprocess.run(
                ['bash', '-c', 'read -p "New name: " name < /dev/tty; echo "$name"'],
                capture_output=True,
                text=True,
                check=False
            )

            new_name = result.stdout.strip()
            
            if not new_name or new_name == old_name:
                print("Cancelled")
                time.sleep(0.5)
                return None
            
            # Keep extension
            old_ext = os.path.splitext(old_name)[1]
            if not new_name.endswith(old_ext):
                new_name += old_ext
            
            new_path = os.path.join(dir_path, new_name)
            
            if os.path.exists(new_path):
                print(f"Error: File already exists: {new_name}")
                time.sleep(1)
                return None
            
            os.rename(image_path, new_path)
            print(f"Renamed to: {new_name}")
            time.sleep(0.5)
            
            return new_path
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
            return None
    
    def _simple_edit(self, image_path):
        """Simple edit without preview."""
        print(f"\nEditing: {os.path.basename(image_path)}")
        print("No preview available. Install chafa: sudo pacman -S chafa")
        print("\n1:Rotate Right  2:Rotate Left  3:Rename  4:Skip")
        print("Action: ", end="", flush=True)
        
        try:
            result = subprocess.run(
                ['bash', '-c', 'read -n 1 -s -r key < /dev/tty; echo "$key"'],
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            choice = result.stdout.strip()
            
            if choice == '1':
                new_path = self._rotate_image(image_path, 'right')
                return (True, new_path) if new_path else (False, image_path)
            elif choice == '2':
                new_path = self._rotate_image(image_path, 'left')
                return (True, new_path) if new_path else (False, image_path)
            elif choice == '3':
                new_path = self._rename_image(image_path)
                return (True, new_path) if new_path else (False, image_path)
            
        except:
            pass
        
        return False, image_path
