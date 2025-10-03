"""Theme learning system - learns from user corrections."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .detector import rgb_distance


class ThemeLearner:
    """Learns theme patterns from user corrections."""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / '.config' / 'omarchy-mover'

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.learning_file = self.config_dir / 'learned_patterns.json'

        self.corrections: List[Dict] = []
        self.load()

    def load(self):
        """Load learned patterns from disk."""
        if not self.learning_file.exists():
            self.corrections = []
            return

        try:
            with open(self.learning_file, 'r') as f:
                data = json.load(f)
                self.corrections = data.get('corrections', [])
        except Exception as e:
            print(f"Warning: Could not load learning data: {e}")
            self.corrections = []

    def save(self):
        """Save learned patterns to disk."""
        try:
            data = {
                'corrections': self.corrections,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save learning data: {e}")

    def record_correction(self, avg_color: Tuple[int, int, int],
                         suggested_theme: str, actual_theme: str):
        """Record a user correction."""
        if suggested_theme == actual_theme:
            return  # No correction needed

        correction = {
            'avg_color': avg_color,
            'suggested_theme': suggested_theme,
            'actual_theme': actual_theme,
            'timestamp': datetime.now().isoformat()
        }

        self.corrections.append(correction)
        self.save()

    def get_learned_theme(self, avg_color: Tuple[int, int, int],
                          suggested_theme: str) -> Optional[str]:
        """
        Check if we've learned a better theme for this color.
        Returns learned theme if found, None otherwise.
        """
        if not self.corrections:
            return None

        # Find corrections for similar colors
        similar_corrections = []
        for correction in self.corrections:
            corr_color = tuple(correction['avg_color'])
            distance = rgb_distance(avg_color, corr_color)

            # If very similar color (within 20 units)
            if distance < 20:
                similar_corrections.append((distance, correction))

        if not similar_corrections:
            return None

        # Use the closest correction
        similar_corrections.sort(key=lambda x: x[0])
        _, closest = similar_corrections[0]

        # If the suggestion matches what was wrong before, use learned theme
        if closest['suggested_theme'] == suggested_theme:
            return closest['actual_theme']

        return None

    def adjust_detection(self, avg_color: Tuple[int, int, int],
                        suggested_theme: str) -> str:
        """
        Adjust theme detection based on learned patterns.
        Returns the adjusted theme (or original if no adjustment).
        """
        learned = self.get_learned_theme(avg_color, suggested_theme)
        return learned if learned else suggested_theme

    def get_stats(self) -> Dict:
        """Get statistics about learned patterns."""
        if not self.corrections:
            return {'total_corrections': 0}

        # Count corrections per theme
        theme_corrections = {}
        for corr in self.corrections:
            actual = corr['actual_theme']
            theme_corrections[actual] = theme_corrections.get(actual, 0) + 1

        # Most recent corrections
        recent = sorted(self.corrections,
                       key=lambda x: x['timestamp'],
                       reverse=True)[:5]

        return {
            'total_corrections': len(self.corrections),
            'theme_corrections': theme_corrections,
            'recent_corrections': recent
        }

    def clear(self):
        """Clear all learned patterns."""
        self.corrections = []
        if self.learning_file.exists():
            self.learning_file.unlink()

    def export_data(self, export_path: Path):
        """Export learned patterns to a file."""
        try:
            with open(export_path, 'w') as f:
                json.dump({
                    'corrections': self.corrections,
                    'exported_at': datetime.now().isoformat()
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting: {e}")
            return False

    def import_data(self, import_path: Path, merge: bool = True):
        """Import learned patterns from a file."""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                imported_corrections = data.get('corrections', [])

            if merge:
                # Merge with existing corrections
                existing_keys = {
                    (tuple(c['avg_color']), c['suggested_theme'], c['actual_theme'])
                    for c in self.corrections
                }

                for corr in imported_corrections:
                    key = (tuple(corr['avg_color']),
                          corr['suggested_theme'],
                          corr['actual_theme'])
                    if key not in existing_keys:
                        self.corrections.append(corr)
            else:
                # Replace all corrections
                self.corrections = imported_corrections

            self.save()
            return True
        except Exception as e:
            print(f"Error importing: {e}")
            return False
