# Claude Text Editor - Setup Instructions

## Quick Setup (After Installation)

### 1. Restart Claude Desktop
Close and reopen Claude Desktop to load the new MCP server.

### 2. Create the macOS Shortcut

1. Open **Shortcuts** app
2. Click **+** to create new shortcut
3. Add these actions:
   - **Receive Text**: From "Quick Actions"
   - **Run Shell Script**: 
     - Shell: `/bin/bash`
     - Pass Input: "to stdin"
     - Script: `/Users/lp698/claude-text-editor/claude_text_shortcut.sh`
4. Settings (⚙️):
   - ✅ Use as Quick Action
   - ✅ Services Menu
   - Name: "Edit with Claude"

### 3. Add Keyboard Shortcut

1. System Settings → Keyboard → Keyboard Shortcuts → Services
2. Find "Edit with Claude" under "Text"
3. Add shortcut: ⌘⇧E (or your preference)

### 4. Start Monitoring in Claude

1. Open Claude Desktop
2. Create/open chat named **"claude_process_text"**
3. Type: `Start monitoring for text files using the start_monitoring tool`
4. Claude confirms: "Started monitoring..."

## You're Ready!

Select text → ⌘⇧E → Wait for notification → ⌘V to paste

## Customize Your Prompt

Edit `~/.claude_text_editor/claude_prompt.txt` to change how Claude processes text.