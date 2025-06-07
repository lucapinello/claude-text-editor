#!/bin/bash
# Notification script for Claude Text Editor

TITLE="${1:-Claude Text Editor}"
MESSAGE="${2:-Text edited and copied to clipboard}"

# Try multiple notification methods

# Method 1: Use osascript with sound (more likely to show)
osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"Glass\""

# Method 2: Also show an alert dialog as fallback (optional - comment out if too intrusive)
# osascript -e "display dialog \"$MESSAGE\" with title \"$TITLE\" buttons {\"OK\"} default button 1 giving up after 3"

# Method 3: Use say command for audio feedback (optional)
# say "Text editing complete"