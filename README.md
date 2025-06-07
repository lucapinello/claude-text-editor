# Claude Text Editor

A seamless text editing system that integrates with Claude Desktop through the Model Context Protocol (MCP). Select text anywhere on macOS, send it to Claude for editing, and automatically receive the edited version.

## Features

- 🚀 **Zero-friction editing**: Select text → Right-click → "Edit with Claude" → Get edited text
- 📁 **File-based processing**: No timeouts, no focus switching required
- 🔄 **Automatic queue management**: Drop files in inbox, get results in outbox
- 🎯 **Customizable prompts**: Define your editing instructions in `claude_prompt.txt`
- 🖥️ **System-wide integration**: Works with any macOS application
- 🔔 **Desktop notifications**: Get notified when text processing is complete
- 📋 **Auto-clipboard**: Edited text is automatically copied to your clipboard
- 🤖 **MCP-powered**: Native integration with Claude Desktop

## Prerequisites

- macOS (tested on macOS 14.x)
- Claude Desktop app installed
- Terminal access
- Internet connection
- Homebrew (optional but recommended for desktop notifications)
  - Install from: https://brew.sh
  - Or run: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

## Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/lucapinello/claude-text-editor.git
cd claude-text-editor

# Run the install script
./install.sh
```

The install script will:
- Check for Python/conda/mamba
- Create the necessary directories
- Set up the Python environment from `environment.yml`
- Install dependencies (including MCP)
- Install `terminal-notifier` for desktop notifications (if Homebrew is installed)
- Configure Claude Desktop
- Copy all files to the correct locations
- Create the default prompt file

**Note**: Desktop notifications require Homebrew. Without it, you'll still get audio feedback (Glass sound) when text is processed.

## Getting Started with Claude Desktop

After installation, you need to initialize the Claude Text Editor in Claude Desktop:

### Initialize Claude Text Editor (Easy Method)

1. **Restart Claude Desktop** after installation
2. **Create a new chat** named `claude_text_editor`
3. **Copy and paste this message** and press Enter:

```
I'm using the Claude Text Editor MCP server. Please continuously monitor the edit queue and automatically process any text files that appear. 

CRITICAL REQUIREMENTS:
- This is a CONTINUOUS, INDEFINITE monitoring task that should NEVER stop
- Do NOT stop monitoring unless explicitly told to stop
- Do NOT provide status updates or explanations unless a file is processed
- Keep the monitoring loop running silently in the background
- Only report when files are found and processed

Process:
1. Check the edit queue using check_edit_queue
2. If there are files, use get_text_to_edit to retrieve each one
3. Edit the text according to the prompt provided
4. Use save_edited_text to save the result with the same filename
5. After processing all files, use wait_for_files (30 seconds)
6. Return to step 1 and repeat FOREVER

```

4. Claude will confirm the tools are available and start monitoring for files
5. **Keep this chat open** while using the text editor - Claude will automatically process files as they arrive

### Testing Your Setup

```bash
# Test with a simple file
echo "This is a test sentance with bad grammer." > ~/.claude_text_editor/inbox/test.txt

# Claude should automatically process it if the chat is monitoring
# Check the result
cat ~/.claude_text_editor/outbox/test.txt
```

## Usage

### Basic Workflow

1. **Keep Claude Desktop open** with the `claude_text_editor` chat active
2. **Use the keyboard shortcut** (⌥⌘.) on any selected text, or drop files in `~/.claude_text_editor/inbox/`
3. **Claude processes automatically** and saves results to `~/.claude_text_editor/outbox/`
4. **Get instant feedback**:
   - Desktop notification appears (requires Homebrew + terminal-notifier)
   - "Glass" sound plays (always works)
   - Text is automatically copied to clipboard

### Using the Client Script

```bash
# Edit text from clipboard
pbpaste | ~/claude-text-editor/claude_text_client.py

# Edit text from a file
cat myfile.txt | ~/claude-text-editor/claude_text_client.py

# Edit with custom timeout
echo "Edit this text" | ~/claude-text-editor/claude_text_client.py --timeout 60

# Edit without copying to clipboard
echo "Edit this text" | ~/claude-text-editor/claude_text_client.py --no-clipboard
```

### Customizing Edit Instructions

Edit `~/.claude_text_editor/claude_prompt.txt` to change how Claude processes your text:

```text
Please edit the following text to:
- Make it more formal and professional
- Fix any technical inaccuracies
- Add relevant examples where appropriate

Text to edit:
```

### System-Wide Text Editing Shortcut

The install script sets up the necessary files. To enable the keyboard shortcut:

#### Option 1: Import Pre-made Shortcut (Easiest)

1. Open **Shortcuts** app
2. **File → Import** or drag `Edit_with_Claude.shortcut` from the project folder
3. The shortcut is already configured and ready to use!

#### Option 2: Create Shortcut Manually

1. Open **Shortcuts** app
2. Click **+** to create new shortcut
3. Add these actions:
   - **Receive Text**: From "Quick Actions"
   - **Run Shell Script**: 
     - Shell: `/bin/bash`
     - Pass Input: "to stdin"
     - Script: `~/claude-text-editor/claude_text_shortcut.sh`
4. Settings (⚙️):
   - ✅ Use as Quick Action
   - ✅ Services Menu
   - Name: "Edit with Claude"

#### Add Keyboard Shortcut

1. System Settings → Keyboard → Keyboard Shortcuts → Services
2. Find "Edit with Claude" under "Text"
3. Add shortcut: ⌥⌘. (Option+Command+Period)

Now you can select text anywhere → ⌥⌘. → Claude processes it → Result is copied to clipboard!

## Architecture

The system consists of several components:

- **MCP Server** (`text-editor-server.py`): Integrates with Claude Desktop
- **File Monitor**: Watches `~/.claude_text_editor/inbox/` for new files
- **Client Script** (`claude_text_client.py`): Command-line interface for text editing
- **Wrapper Script** (`mcp-server-wrapper.sh`): Manages Python environment

### File Flow

```
User Input → inbox/ → Claude processes → outbox/ → User receives output
```

## Troubleshooting

### Server won't connect
1. Check the logs: `tail -100 ~/Library/Logs/Claude/mcp-server-text-editor.log`
2. Verify conda environment: `conda activate claude-text-editor && which python`
3. Test the server directly: `~/claude-text-editor/mcp-server-wrapper.sh`

### Tools not available in Claude Desktop
1. Ensure Claude Desktop was restarted after configuration
2. Check that the config file path is correct for your username
3. Verify the wrapper script is executable
4. Look for error messages in the logs

### Permission errors
```bash
chmod +x ~/claude-text-editor/mcp-server-wrapper.sh
chmod +x ~/claude-text-editor/claude_text_client.py
```

### Python or module not found
1. Ensure conda is properly initialized in your shell
2. Verify the environment is activated: `conda activate claude-text-editor`
3. Check that MCP is installed: `pip list | grep mcp`

## Development

### Project Structure
```
~/claude-text-editor/
├── text-editor-server.py           # MCP server implementation
├── mcp-server-wrapper.sh           # Environment wrapper
├── claude_text_client.py           # Command-line client
└── ~/.claude_text_editor/
    ├── inbox/                      # Drop text files here
    ├── outbox/                     # Receive edited files here
    └── claude_prompt.txt           # Editing instructions
```

### Extending the System

You can extend the system by:
1. Adding new tools to the MCP server
2. Creating additional client scripts for specific workflows
3. Integrating with other applications via AppleScript or shell scripts

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by [Claude Desktop](https://claude.ai/)
- Python environment management by [Miniforge](https://github.com/conda-forge/miniforge)