"""Image preview generation for fzf."""

import shlex
import shutil

def has_preview_support():
    """Check if system has image preview tools available."""
    tools = ['chafa', 'viu', 'kitty']
    for tool in tools:
        if shutil.which(tool):
            return tool
    return None

def generate_preview_command(preview_dir, tool=None):
    """Generate preview command for fzf based on available tools."""
    if tool is None:
        tool = has_preview_support()

    if not tool:
        return None

    if tool == 'chafa':
        # Use a wrapper script approach - pass entry as argument to avoid quoting hell
        # The $1 will be the entry passed by fzf via {}
        script = f'''entry="$1"
if [[ "$entry" == "[DONE]"* ]] || [[ "$entry" == "[CLEAR]"* ]] || [[ "$entry" == "[EDIT]"* ]] || [[ "$entry" == "---" ]] || [[ "$entry" == "[UP]"* ]]; then
    echo "Select an image to preview"
    exit 0
fi
filename=$(echo "$entry" | sed 's/^\\[.*\\] //' | sed 's/ (.*$//')
fullpath="{preview_dir}/$filename"
if [[ "$entry" == *"/" ]]; then
    echo "Directory: $filename"
    ls -lah "$fullpath" 2>/dev/null | head -20
    exit 0
fi
if [ -f "$fullpath" ]; then
    echo "File: $filename"
    command -v identify &>/dev/null && identify -format "%wx%h | %m | %b" "$fullpath" 2>/dev/null

    # Detect theme using Python
    theme_info=$(python3 -c "
import sys
sys.path.insert(0, '{shlex.quote(preview_dir)}')
try:
    from omarchy_mover.detector import analyze_image
    result = analyze_image('$fullpath')
    if result:
        conf_map = {{'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}}
        symbol = conf_map.get(result['confidence'], '[?]')
        print(f\\\"Theme: {{symbol}} {{result['suggested_theme']}} (dist: {{result['distance']:.1f}})\\\")
except Exception:
    pass
" 2>/dev/null)
    [ -n "$theme_info" ] && echo "$theme_info"

    echo ""
    width="${{FZF_PREVIEW_COLUMNS:-100}}"
    height="${{FZF_PREVIEW_LINES:-50}}"
    chafa --size "$width"x"$height" --format symbols --symbols vhalf,wedge --colors full --dither diffusion "$fullpath" 2>/dev/null
else
    echo "File not found: $fullpath"
    echo "Entry was: $entry"
    ls -la "{preview_dir}" 2>&1 | head -5
fi'''
        # Return command that passes {} as argument to bash script
        return f"bash -c {shlex.quote(script)} -- {{}}"
    
    elif tool == 'viu':
        script = f'''entry="$1"
if [[ "$entry" == "[DONE]"* ]] || [[ "$entry" == "[CLEAR]"* ]] || [[ "$entry" == "[EDIT]"* ]] || [[ "$entry" == "---" ]] || [[ "$entry" == "[UP]"* ]]; then
    echo "Select an image to preview"
    exit 0
fi
filename=$(echo "$entry" | sed 's/^\\[.*\\] //' | sed 's/ (.*$//')
fullpath="{preview_dir}/$filename"
if [[ "$entry" == *"/" ]]; then
    echo "Directory: $filename"
    ls -lah "$fullpath" 2>/dev/null | head -20
    exit 0
fi
if [ -f "$fullpath" ]; then
    echo "File: $filename"
    command -v identify &>/dev/null && identify -format "%wx%h | %m | %b" "$fullpath" 2>/dev/null

    # Detect theme using Python
    theme_info=$(python3 -c "
import sys
sys.path.insert(0, '{shlex.quote(preview_dir)}')
try:
    from omarchy_mover.detector import analyze_image
    result = analyze_image('$fullpath')
    if result:
        conf_map = {{'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}}
        symbol = conf_map.get(result['confidence'], '[?]')
        print(f\\\"Theme: {{symbol}} {{result['suggested_theme']}} (dist: {{result['distance']:.1f}})\\\")
except Exception:
    pass
" 2>/dev/null)
    [ -n "$theme_info" ] && echo "$theme_info"

    echo ""
    viu -t "$fullpath" 2>/dev/null
else
    echo "File not found: $fullpath"
fi'''
        return f"bash -c {shlex.quote(script)} -- {{}}"

    elif tool == 'kitty':
        script = f'''entry="$1"
if [[ "$entry" == "[DONE]"* ]] || [[ "$entry" == "[CLEAR]"* ]] || [[ "$entry" == "[EDIT]"* ]] || [[ "$entry" == "---" ]] || [[ "$entry" == "[UP]"* ]]; then
    echo "Select an image to preview"
    exit 0
fi
filename=$(echo "$entry" | sed 's/^\\[.*\\] //' | sed 's/ (.*$//')
fullpath="{preview_dir}/$filename"
if [[ "$entry" == *"/" ]]; then
    echo "Directory: $filename"
    exit 0
fi
if [ -f "$fullpath" ]; then
    echo "File: $filename"

    # Detect theme using Python
    theme_info=$(python3 -c "
import sys
sys.path.insert(0, '{shlex.quote(preview_dir)}')
try:
    from omarchy_mover.detector import analyze_image
    result = analyze_image('$fullpath')
    if result:
        conf_map = {{'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}}
        symbol = conf_map.get(result['confidence'], '[?]')
        print(f\\\"Theme: {{symbol}} {{result['suggested_theme']}} (dist: {{result['distance']:.1f}})\\\")
except Exception:
    pass
" 2>/dev/null)
    [ -n "$theme_info" ] && echo "$theme_info"

    echo ""
    kitty +kitten icat --clear --transfer-mode=memory --stdin=no "$fullpath" 2>/dev/null
else
    echo "File not found: $fullpath"
fi'''
        return f"bash -c {shlex.quote(script)} -- {{}}"

    return None
