"""Interactive directory browser."""

import os
import traceback
from .fzf import select_with_fzf
from .preview import has_preview_support, generate_preview_command
from .viewer import ImageViewer

def list_dir_contents(path, selected_images=None):
    """List directories and image files in path."""
    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
    entries = []
    selected_set = set(selected_images) if selected_images else set()

    try:
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                entries.append(f'[DIR] {item}/')
            elif full_path.lower().endswith(IMAGE_EXTS):
                try:
                    size_bytes = os.path.getsize(full_path)
                    if size_bytes < 1024:
                        size_str = f"{size_bytes}B"
                    elif size_bytes < 1024 * 1024:
                        size_str = f"{size_bytes / 1024:.1f}KB"
                    else:
                        size_str = f"{size_bytes / (1024 * 1024):.1f}MB"

                    # Add checkmark if already selected
                    checkmark = '✓ ' if full_path in selected_set else ''
                    entries.append(f'[IMG] {checkmark}{item} ({size_str})')
                except:
                    checkmark = '✓ ' if full_path in selected_set else ''
                    entries.append(f'[IMG] {checkmark}{item}')

        if path != os.path.expanduser('~') and path != '/':
            entries.insert(0, '[UP]  ../')

        return entries
    except PermissionError:
        print(f'Warning: Permission denied: {path}')
        return []
    except OSError as e:
        print(f'Warning: Error listing {path}: {e}')
        return []

def clean_entry(entry):
    """Remove prefixes, checkmarks, and size info from entry."""
    parts = entry.split(maxsplit=1)
    if len(parts) > 1:
        filename = parts[1]
        # Remove checkmark if present
        if filename.startswith('✓ '):
            filename = filename[2:]
        # Remove size info in parentheses
        if '(' in filename and filename.endswith(')'):
            filename = filename[:filename.rfind('(')].strip()
        return filename
    return entry

class ImageBrowser:
    """Interactive image browser with persistent state."""
    
    def __init__(self, start_path='~', enable_preview=True):
        self.current_path = os.path.abspath(os.path.expanduser(start_path))
        self.selected_images = []
        self.enable_preview = enable_preview and has_preview_support() is not None
        self.viewer = ImageViewer()
        
        if self.enable_preview:
            tool = has_preview_support()
            print(f'Image preview enabled (using {tool})')
            print('Tip: Install imagemagick for image info: sudo pacman -S imagemagick')
        else:
            print('Image preview not available.')
            print('Install chafa for best results: sudo pacman -S chafa')
    
    def run(self):
        """Main browsing loop."""
        while True:
            entries = list_dir_contents(self.current_path, self.selected_images)
            
            if not entries:
                print(f'Empty directory: {self.current_path}')
                if not self._go_back():
                    break
                continue
            
            # Add control options if images are selected
            if self.selected_images:
                entries.insert(0, f'[DONE] Process {len(self.selected_images)} selected image(s)')
                entries.insert(1, '[CLEAR] Clear selection')
                entries.insert(2, '[EDIT] View/Edit selected images')
                entries.insert(3, '---')
            
            # Build prompt
            count_str = f' [{len(self.selected_images)} selected]' if self.selected_images else ''
            prompt = f'{os.path.basename(self.current_path)}{count_str}> '
            
            # Generate preview command
            preview_cmd = None
            if self.enable_preview:
                preview_cmd = generate_preview_command(self.current_path)
                if not preview_cmd:
                    print(f"Warning: Could not generate preview command for {self.current_path}")
            
            selections = select_with_fzf(
                entries,
                prompt,
                multi=True,
                preview=preview_cmd
            )
            
            if not selections:
                # ESC pressed
                if self.selected_images:
                    action = self._show_action_menu()
                    if action == 'process':
                        return self.selected_images
                    elif action == 'clear':
                        self._clear_selection()
                    elif action == 'exit':
                        return []
                else:
                    return []
            else:
                # Handle selections
                if any(sel.startswith('[DONE]') for sel in selections):
                    return self.selected_images
                elif any(sel.startswith('[CLEAR]') for sel in selections):
                    self._clear_selection()
                    continue
                elif any(sel.startswith('[EDIT]') for sel in selections):
                    self._edit_images()
                    continue
                else:
                    self._handle_selections(selections)
    
    def _edit_images(self):
        """Edit selected images with live viewer."""
        if not self.selected_images:
            print("\n⚠️  No images selected. Please select images first using TAB.")
            print("Press ENTER to continue...")
            input()
            return

        print(f"\n📝 Editing {len(self.selected_images)} image(s)...")
        print("Press Ctrl+C to stop editing\n")

        updated_paths = []

        for i, img_path in enumerate(self.selected_images, 1):
            try:
                # Verify file exists
                if not os.path.isfile(img_path):
                    print(f"Warning: File not found: {img_path}")
                    updated_paths.append(img_path)
                    continue

                print(f"\n[{i}/{len(self.selected_images)}] Viewing: {os.path.basename(img_path)}")
                modified, new_path = self.viewer.view_and_edit(img_path)

                if new_path and os.path.isfile(new_path):
                    updated_paths.append(new_path)
                else:
                    updated_paths.append(img_path)

            except KeyboardInterrupt:
                print("\nEditing cancelled")
                # Add remaining images unchanged
                updated_paths.extend(self.selected_images[i:])
                break
            except Exception as e:
                print(f"Error editing {os.path.basename(img_path)}: {e}")
                traceback.print_exc()
                updated_paths.append(img_path)

        # Update selected images with new paths
        self.selected_images = updated_paths
        print(f"\nEdit complete. {len(self.selected_images)} image(s) selected.")
    
    def _handle_selections(self, selections):
        """Process user selections."""
        IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        
        for sel in selections:
            if sel == '---':
                continue
            
            clean_sel = clean_entry(sel)
            full_path = os.path.join(self.current_path, clean_sel.rstrip('/'))
            
            if clean_sel == '../':
                self._go_back()
                return
            elif clean_sel.endswith('/'):
                if os.path.isdir(full_path):
                    self.current_path = full_path
                    return
            else:
                if os.path.isfile(full_path) and full_path.lower().endswith(IMAGE_EXTS):
                    if full_path not in self.selected_images:
                        self.selected_images.append(full_path)
                        print(f'Added: {os.path.basename(full_path)}')
                    else:
                        print(f'Already selected: {os.path.basename(full_path)}')
    
    def _go_back(self):
        """Navigate to parent directory."""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            return True
        return False
    
    def _show_action_menu(self):
        """Show action menu."""
        actions = [
            f'Process {len(self.selected_images)} image(s)',
            'View/Edit images',
            'Continue selecting',
            'Clear selection',
            'Exit without processing'
        ]
        
        result = select_with_fzf(actions, 'Action: ')
        
        if not result:
            return 'continue'
        elif result.startswith('Process'):
            return 'process'
        elif result.startswith('View'):
            self._edit_images()
            return 'continue'
        elif result.startswith('Continue'):
            return 'continue'
        elif result.startswith('Clear'):
            return 'clear'
        else:
            return 'exit'
    
    def _clear_selection(self):
        """Clear all selected images."""
        count = len(self.selected_images)
        self.selected_images.clear()
        print(f'Cleared {count} image(s)')
