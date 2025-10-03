"""Configuration management for Omarchy Image Mover."""

import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "base_dir": "~/.local/share/omarchy/themes",
    "history_file": "~/.local/share/omarchy/mover_history.json",
    "max_history": 100,
    "custom_themes": {},
    "default_mode": "auto",
    "confidence_threshold": 50,
    "auto_confirm_high_confidence": True,
}

class Config:
    """Manage configuration for the image mover."""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.expanduser("~/.config/omarchy/mover.json")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load config from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current config to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Could not save config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get config value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value."""
        self.config[key] = value
    
    def add_custom_theme(self, name, rgb):
        """Add a custom theme."""
        if "custom_themes" not in self.config:
            self.config["custom_themes"] = {}
        self.config["custom_themes"][name] = rgb
        return self.save_config()
    
    def remove_custom_theme(self, name):
        """Remove a custom theme."""
        if name in self.config.get("custom_themes", {}):
            del self.config["custom_themes"][name]
            return self.save_config()
        return False
    
    def get_all_themes(self):
        """Get both default and custom themes."""
        from .themes import THEMES
        all_themes = THEMES.copy()
        all_themes.update(self.config.get("custom_themes", {}))
        return all_themes
    
    def reset_to_defaults(self):
        """Reset config to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()

    def export_themes(self, export_path):
        """Export custom themes and learned patterns."""
        from .learning import ThemeLearner

        learner = ThemeLearner()

        export_data = {
            "custom_themes": self.config.get("custom_themes", {}),
            "learned_patterns": learner.corrections,
            "exported_at": Path(export_path).name,
            "config_version": "1.0"
        }

        try:
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"✓ Exported themes to: {export_path}")
            return True
        except Exception as e:
            print(f"Error exporting themes: {e}")
            return False

    def import_themes(self, import_path, merge=True):
        """Import custom themes and learned patterns."""
        from .learning import ThemeLearner

        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)

            custom_themes = import_data.get("custom_themes", {})
            learned_patterns = import_data.get("learned_patterns", [])

            if merge:
                # Merge custom themes
                existing_themes = self.config.get("custom_themes", {})
                existing_themes.update(custom_themes)
                self.config["custom_themes"] = existing_themes
            else:
                # Replace custom themes
                self.config["custom_themes"] = custom_themes

            self.save_config()

            # Import learned patterns
            if learned_patterns:
                learner = ThemeLearner()
                learner.corrections.extend(learned_patterns)
                learner.save()

            print(f"✓ Imported {len(custom_themes)} themes and {len(learned_patterns)} learned patterns")
            return True

        except Exception as e:
            print(f"Error importing themes: {e}")
            return False

def create_default_config():
    """Create default config file."""
    config = Config()
    config.save_config()
    print(f"Created default config at: {config.config_path}")
    return config.config_path
