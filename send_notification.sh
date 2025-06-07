#!/bin/bash
# Simple notification sender for Claude Text Editor

TITLE="${1:-Claude Text Editor}"
MESSAGE="${2:-Text edited and copied to clipboard!}"

# Method 1: Try terminal-notifier if installed
if command -v terminal-notifier &> /dev/null; then
    terminal-notifier -title "$TITLE" -message "$MESSAGE" -sound Glass
    exit 0
fi

# Method 2: Use osascript with an app context that might trigger permission
osascript <<EOF
tell application id "com.apple.SystemEvents"
    display notification "$MESSAGE" with title "$TITLE" sound name "Glass"
end tell
EOF

# Also play sound as feedback
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true