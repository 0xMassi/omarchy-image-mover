"""History tracking and undo functionality."""

import json
import os
import shutil
from datetime import datetime

class History:
    """Track move operations and enable undo."""
    
    def __init__(self, history_file=None, max_entries=100):
        if history_file is None:
            history_file = os.path.expanduser("~/.local/share/omarchy/mover_history.json")
        
        self.history_file = history_file
        self.max_entries = max_entries
        self.entries = self._load_history()
    
    def _load_history(self):
        """Load history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            # Keep only last max_entries
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.entries, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save history: {e}")
            return False
    
    def add_entry(self, source, destination, theme, operation='move'):
        """Add a history entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'destination': destination,
            'theme': theme,
            'operation': operation,
            'filename': os.path.basename(source)
        }
        self.entries.append(entry)
        return self._save_history()
    
    def get_recent(self, n=10):
        """Get n most recent entries."""
        return self.entries[-n:] if self.entries else []
    
    def undo_last(self):
        """Undo the last operation."""
        if not self.entries:
            return False, "No operations to undo"
        
        last_entry = self.entries[-1]
        source = last_entry['source']
        destination = last_entry['destination']
        operation = last_entry['operation']
        
        try:
            if operation == 'move':
                # Move file back to original location
                if os.path.exists(destination):
                    # Recreate source directory if needed
                    os.makedirs(os.path.dirname(source), exist_ok=True)
                    shutil.move(destination, source)
                    self.entries.pop()
                    self._save_history()
                    return True, f"Restored: {os.path.basename(source)}"
                else:
                    return False, f"File not found: {destination}"
            
            elif operation == 'copy':
                # Remove the copy
                if os.path.exists(destination):
                    os.remove(destination)
                    self.entries.pop()
                    self._save_history()
                    return True, f"Removed copy: {os.path.basename(destination)}"
                else:
                    return False, f"File not found: {destination}"
            
            return False, "Unknown operation type"
        
        except Exception as e:
            return False, f"Undo failed: {e}"
    
    def undo_by_index(self, index):
        """Undo a specific operation by index."""
        if index < 0 or index >= len(self.entries):
            return False, "Invalid index"
        
        entry = self.entries[index]
        source = entry['source']
        destination = entry['destination']
        operation = entry['operation']
        
        try:
            if operation == 'move':
                if os.path.exists(destination):
                    os.makedirs(os.path.dirname(source), exist_ok=True)
                    shutil.move(destination, source)
                    self.entries.pop(index)
                    self._save_history()
                    return True, f"Restored: {os.path.basename(source)}"
            
            elif operation == 'copy':
                if os.path.exists(destination):
                    os.remove(destination)
                    self.entries.pop(index)
                    self._save_history()
                    return True, f"Removed copy: {os.path.basename(destination)}"
            
            return False, "File not found"
        
        except Exception as e:
            return False, f"Undo failed: {e}"
    
    def clear_history(self):
        """Clear all history."""
        self.entries = []
        return self._save_history()
    
    def format_entry(self, entry):
        """Format a history entry for display."""
        timestamp = datetime.fromisoformat(entry['timestamp'])
        time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        op = entry['operation'].upper()
        return f"[{time_str}] {op}: {entry['filename']} -> {entry['theme']}"
