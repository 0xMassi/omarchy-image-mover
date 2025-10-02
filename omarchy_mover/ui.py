"""User interface and navigation using FZF."""

import os
import subprocess
import sys

def select_with_fzf(options, prompt='Select: ', multi=False, preview=None):
    """
    Present options to user using fzf.
    Returns list if multi=True, single string otherwise.
    """
    if not options:
        return [] if multi else ''
    
    input_data = '\n'.join(options) + '\n'
    cmd = [
        'fzf',
        '--prompt', prompt,
        '--height', '40%',
        '--border',
        '--no-sort',
        '--reverse',
        '--info', 'inline'
    ]
    
    if multi:
        cmd.extend([
            '--multi',
            '--bind', 'ctrl-a:select-all',
            '--bind', 'ctrl-d:deselect-all'
        ])
    
    if preview:
        cmd.extend(['--preview', preview])
    
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        selections = [s.strip() for s in result.stdout.split('\n') if s.strip()]
        return selections if multi else (selections[0] if selections else '')
    except subprocess.CalledProcessError:
        return [] if multi else ''
    except FileNotFoundError:
        print('Error: fzf not installed. Install: sudo pacman -S fzf (Arch) or sudo apt install fzf (Debian/Ubuntu)')
        sys.exit(1)

def list_dir_contents(path):
    """List directories and image files in path."""
    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
    entries = []
    
    try:
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                entries.append(f'[DIR] {item}/')
            elif full_path.lower().endswith(IMAGE_EXTS):
                entries.append(f'[IMG] {item}')
        
        # Add parent directory navigation
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
    """Remove prefixes from entry."""
    parts = entry.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else entry

class ImageBrowser:
    """Interactive image browser with persistent state."""
    
    def __init__(self, start_path='~'):
        self.current_path = os.path.abspath(os.path.expanduser(start_path))
        self.selected_images = []
    
    def run(self):
        """Main browsing loop."""
        while True:
            entries = list_dir_contents(self.current_path)
            
            if not entries:
                print(f'Empty directory: {self.current_path}')
                if not self._go_back():
                    break
                continue
            
            # Add DONE option if images are selected
            if self.selected_images:
                done_option = f'[DONE] Process {len(self.selected_images)} selected image(s)'
                entries.insert(0, done_option)
                entries.insert(1, '[CLEAR] Clear selection')
                entries.insert(2, '---')
            
            # Show current selection count in prompt
            count_str = f' [{len(self.selected_images)} selected]' if self.selected_images else ''
            prompt = f'{os.path.basename(self.current_path)}{count_str}> '
            
            selections = select_with_fzf(entries, prompt, multi=True)
            
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
                # Check if DONE or CLEAR was selected
                if any(sel.startswith('[DONE]') for sel in selections):
                    return self.selected_images
                elif any(sel.startswith('[CLEAR]') for sel in selections):
                    self._clear_selection()
                    continue
                else:
                    self._handle_selections(selections)
    
    def _handle_selections(self, selections):
        """Process user selections (files or directories)."""
        IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        
        for sel in selections:
            # Skip separator
            if sel == '---':
                continue
                
            clean_sel = clean_entry(sel)
            full_path = os.path.join(self.current_path, clean_sel.rstrip('/'))
            
            if clean_sel == '../':
                self._go_back()
                return
            elif clean_sel.endswith('/'):
                # Navigate into directory
                if os.path.isdir(full_path):
                    self.current_path = full_path
                    return
            else:
                # It's a file
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
        """Show action menu when ESC is pressed with selections."""
        actions = [
            f'Process {len(self.selected_images)} image(s)',
            'Continue selecting',
            'Clear selection',
            'Exit without processing'
        ]
        
        result = select_with_fzf(actions, 'Action: ')
        
        if not result:
            return 'continue'
        elif result.startswith('Process'):
            return 'process'
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

def confirm(message):
    """Ask yes/no confirmation."""
    result = select_with_fzf(['yes', 'no'], f'{message} ')
    return result == 'yes'
