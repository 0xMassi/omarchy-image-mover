"""FZF wrapper functions."""

import subprocess
import sys

def select_with_fzf(options, prompt='Select: ', multi=False, preview=None, preview_window='right:70%:wrap'):
    """
    Present options to user using fzf.
    Returns list if multi=True, single string otherwise.
    Raises KeyboardInterrupt if user presses Ctrl+C.
    """
    if not options:
        return [] if multi else ''

    input_data = '\n'.join(options) + '\n'
    cmd = [
        'fzf',
        '--prompt', prompt,
        '--height', '100%',  # Use full height
        '--border',
        '--no-sort',
        '--reverse',
        '--info', 'inline',
        '--ansi'
    ]

    if multi:
        cmd.extend([
            '--multi',
            '--bind', 'ctrl-a:select-all',
            '--bind', 'ctrl-d:deselect-all'
        ])

    if preview:
        cmd.extend(['--preview', preview, '--preview-window', preview_window])

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
    except subprocess.CalledProcessError as e:
        # Exit code 130 means Ctrl+C was pressed
        if e.returncode == 130:
            raise KeyboardInterrupt
        return [] if multi else ''
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt to propagate it
        raise
    except FileNotFoundError:
        print('Error: fzf not installed')
        print('Install: sudo pacman -S fzf')
        sys.exit(1)

def confirm(message, yes_text='Yes', no_text='No'):
    """
    Ask yes/no confirmation with custom text options.
    Raises KeyboardInterrupt if user presses Ctrl+C.

    Args:
        message: The question to ask
        yes_text: Custom text for yes option (default: 'Yes')
        no_text: Custom text for no option (default: 'No')

    Returns:
        True if yes option selected, False otherwise
    """
    result = select_with_fzf([yes_text, no_text], f'{message} ')
    return result == yes_text
