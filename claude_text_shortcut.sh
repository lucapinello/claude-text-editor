#!/bin/bash
#
# Claude Text Editor Shortcut Wrapper
# This script is called by the macOS shortcut to process selected text
#

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get selected text from the shortcut (passed as argument or stdin)
if [ $# -gt 0 ]; then
    # Text passed as argument
    SELECTED_TEXT="$1"
else
    # Text passed via stdin
    SELECTED_TEXT=$(cat)
fi

# Check if we have text
if [ -z "$SELECTED_TEXT" ]; then
    osascript -e 'display notification "No text selected" with title "Claude Text Editor"'
    exit 1
fi

# Process the text using the installed client
echo "$SELECTED_TEXT" | ~/claude-text-editor/claude_text_client.py

# Exit with the same code as the client
exit $?