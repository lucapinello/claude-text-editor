#!/bin/bash
# Simple notification sender for Claude Text Editor

TITLE="${1:-Claude Text Editor}"
MESSAGE="${2:-Text edited and copied to clipboard!}"

# Method 1: Try terminal-notifier if installed
if command -v terminal-notifier &> /dev/null; then
    terminal-notifier -title "$TITLE" -message "$MESSAGE" -sound Glass
    exit 0
fi

# Method 2: Use osascript with proper escaping
# Use -e with separate arguments to avoid injection
osascript \
    -e 'on run argv' \
    -e '    tell application id "com.apple.SystemEvents"' \
    -e '        display notification (item 2 of argv) with title (item 1 of argv) sound name "Glass"' \
    -e '    end tell' \
    -e 'end run' \
    -- "$TITLE" "$MESSAGE"

# Also play sound as feedback
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true