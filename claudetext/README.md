# Claude Text Editor

A seamless macOS text editing integration that allows you to edit any selected text using Claude with a simple right-click or keyboard shortcut.

## Features

- 🚀 **Zero-interaction workflow**: Select text → Keyboard shortcut → Get edited text in clipboard
- 🌍 **System-wide**: Works in any macOS application
- 📁 **File-based architecture**: No timeouts, fully event-driven
- 🔄 **Background processing**: No window switching or focus changes
- 📝 **Customizable prompts**: Edit how Claude processes your text
- 🔔 **Smart notifications**: Know when your text is ready
- 💬 **Single chat session**: Reuses the same Claude chat to avoid clutter

## How It Works

1. **File Monitoring**: MCP server monitors `~/.claude_text_editor/inbox/` for new text files
2. **Automatic Processing**: When a file appears, Claude processes it automatically
3. **Response Handling**: Processed text is saved to `~/.claude_text_editor/outbox/`
4. **Clipboard Integration**: Client copies the result to clipboard and cleans up files
5. **User Notification**: macOS notification when complete

## Quick Start

### Installation (5 minutes)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/claude-text-editor.git
   cd claude-text-editor/claudetext
   ```

2. **Run the installer**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Restart Claude Desktop**

4. **Create the macOS Shortcut**:
   - Open the Shortcuts app
   - Click the "+" to create a new shortcut
   - Add the following actions:
     - **Add "Receive Text" action**:
       - Click "Receive" and select "Text"
       - From: "Quick Actions"
     - **Add "Run Shell Script" action**:
       - Shell: `/bin/bash`
       - Pass Input: "to stdin"
       - Script: `/Users/lp698/claude-text-editor/claude_text_shortcut.sh`
   - Click the settings icon (⚙️) at the top
   - Check "Use as Quick Action"
   - Check "Services Menu"
   - Name it: "Edit with Claude"

5. **Add keyboard shortcut** (optional):
   - System Settings → Keyboard → Keyboard Shortcuts → Services
   - Find "Edit with Claude" under "Text" → Add shortcut (e.g., ⌘⇧E)

### First-Time Setup in Claude

1. Open Claude Desktop
2. Create a new chat and name it **"claude_process_text"** (important!)
3. Type: `Start monitoring for text files using the start_monitoring tool`
4. Claude will confirm monitoring has started

## Usage

1. Select any text in any application
2. Use your keyboard shortcut (e.g., ⌘⇧E) or right-click → Services → "Edit with Claude"
3. Wait for the notification (usually 2-5 seconds)
4. Press ⌘V to paste the edited text

## Customization

### Edit Processing Prompt

The default prompt improves grammar, clarity, and flow. To customize how Claude processes text:

1. Edit `~/.claude_text_editor/claude_prompt.txt`
2. Save your changes
3. New edits will use your custom prompt

Example prompts:
- **Formal tone**: "Rewrite in a professional, formal tone:"
- **Simplify**: "Simplify this text for a general audience:"
- **Translate**: "Translate to Spanish:"

## File Structure

```
~/.claude_text_editor/
├── inbox/              # Text files appear here for processing
├── outbox/             # Processed responses appear here
├── claude_prompt.txt   # Your custom prompt template
└── [temporary files]   # Automatically cleaned up
```

## Troubleshooting

### Claude doesn't respond
- Ensure Claude Desktop is running
- Check that you've started monitoring in the "claude_process_text" chat
- Verify MCP server is connected (look for text-editor in Claude's tools)

### Server disconnected
- Restart Claude Desktop
- Check logs at `~/Library/Logs/Claude/mcp-server-text-editor.log`

### No notification appears
- Check System Settings → Notifications → Shortcuts
- Ensure notifications are enabled

### Keyboard shortcut doesn't work
- Verify the shortcut is properly configured in System Settings
- Make sure text is actually selected before triggering

## Requirements

- macOS 10.15 or later
- Python 3.10+ (or conda/mamba)
- Claude Desktop app
- MCP Python package

### Python Installation Options

The installer will automatically detect and use:
1. **mamba/conda** (preferred) - Creates a Python 3.11 environment
2. **System Python** - Must be 3.10 or newer

If you need to install Python:
- **Recommended**: Install [Miniforge](https://github.com/conda-forge/miniforge) for mamba
- **Alternative**: `brew install python@3.11`

## Architecture

### Components

1. **MCP Server** (`text-editor-server.py`): 
   - Monitors inbox folder for new files
   - Processes text with Claude
   - Saves responses to outbox

2. **Client Script** (`claude_text_client.py`):
   - Creates text files in inbox
   - Monitors for responses
   - Handles clipboard and notifications

3. **Shortcut Wrapper** (`claude_text_shortcut.sh`):
   - Receives text from macOS shortcuts
   - Passes to client script

4. **Configuration**:
   - `claude_prompt.txt`: Customizable processing instructions
   - Claude Desktop MCP configuration

## Advanced Usage

### Multiple Processing Styles

Create different shortcuts with custom prompts:
1. Copy `claude_prompt.txt` to `claude_prompt_formal.txt`
2. Create a new shortcut that modifies the prompt before processing
3. Assign different keyboard shortcuts for each style

### Command Line Usage

Process text directly from terminal:
```bash
echo "Your text here" | /Users/lp698/claude-text-editor/claude_text_shortcut.sh
```

## Uninstall

To remove Claude Text Editor:
```bash
rm -rf ~/claude-text-editor
rm -rf ~/.claude_text_editor
# Remove the MCP server entry from Claude Desktop settings
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.