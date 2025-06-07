#!/bin/bash
# Claude Text Editor - Uninstallation Script

echo "Claude Text Editor Uninstaller"
echo "==============================="
echo ""
echo "This will remove:"
echo "  - Claude Text Editor installation directory"
echo "  - Conda/virtual environment"
echo "  - MCP server configuration from Claude Desktop"
echo "  - Inbox/outbox directories and files"
echo "  - macOS Shortcuts (if you created them)"
echo ""
read -p "Do you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "Starting uninstallation..."

# 1. Remove from Claude Desktop configuration
echo "Removing Claude Text Editor from Claude Desktop configuration..."
CLAUDE_CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    # Create a Python script to safely remove our server
    cat > /tmp/remove_claude_text_editor.py << 'PYTHON_SCRIPT'
import json
import sys
import os

config_file = sys.argv[1]

if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Remove text-editor from mcpServers if it exists
        if "mcpServers" in config and "text-editor" in config["mcpServers"]:
            del config["mcpServers"]["text-editor"]
            
            # If mcpServers is now empty, remove it
            if not config["mcpServers"]:
                del config["mcpServers"]
            
            # Write the updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✓ Removed text-editor from Claude config")
        else:
            print("✓ text-editor not found in Claude config")
    except Exception as e:
        print(f"⚠️  Error updating Claude config: {e}")
else:
    print("✓ No Claude config file found")
PYTHON_SCRIPT

    python3 /tmp/remove_claude_text_editor.py "$CLAUDE_CONFIG_FILE"
    rm -f /tmp/remove_claude_text_editor.py
else
    echo "✓ No Claude config file found"
fi

# 2. Remove conda environment if it exists
if command -v conda &> /dev/null || command -v mamba &> /dev/null; then
    echo "Checking for conda environment..."
    if conda env list | grep -q "claude-text-editor"; then
        echo "Removing conda environment 'claude-text-editor'..."
        conda env remove -n claude-text-editor -y 2>/dev/null || mamba env remove -n claude-text-editor -y 2>/dev/null
        echo "✓ Conda environment removed"
    else
        echo "✓ No conda environment found"
    fi
fi

# 3. Remove installation directory
if [ -d ~/claude-text-editor ]; then
    echo "Removing installation directory..."
    rm -rf ~/claude-text-editor
    echo "✓ Installation directory removed"
else
    echo "✓ Installation directory not found"
fi

# 4. Ask about data directories
echo ""
read -p "Do you want to remove all processed text files in ~/.claude_text_editor? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d ~/.claude_text_editor ]; then
        # Backup prompt file if it was customized
        if [ -f ~/.claude_text_editor/claude_prompt.txt ]; then
            DEFAULT_PROMPT="Process the following text according to these instructions:

1. Fix any grammar or spelling errors
2. Improve clarity and conciseness
3. Maintain the original tone and intent
4. Return only the processed text without explanations
5. Please consider specific instructions contained in parenthesis e.g. {} at the start or at the end of the text. It is IMPERATIVE to follow the instructions provided to formulate your response, so please pay attention to what the user is asking. Otherwise ignore this point.

Text to process:"
            
            CURRENT_PROMPT=$(cat ~/.claude_text_editor/claude_prompt.txt 2>/dev/null)
            
            if [ "$CURRENT_PROMPT" != "$DEFAULT_PROMPT" ]; then
                cp ~/.claude_text_editor/claude_prompt.txt ~/claude_prompt_backup_$(date +%Y%m%d_%H%M%S).txt
                echo "✓ Custom prompt backed up to ~/claude_prompt_backup_*.txt"
            fi
        fi
        
        rm -rf ~/.claude_text_editor
        echo "✓ Data directories removed"
    else
        echo "✓ No data directories found"
    fi
else
    echo "✓ Keeping data directories"
fi

# 5. Remove terminal-notifier if user wants
if command -v terminal-notifier &> /dev/null; then
    echo ""
    read -p "Do you want to uninstall terminal-notifier? (y/N) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            brew uninstall terminal-notifier
            echo "✓ terminal-notifier uninstalled"
        else
            echo "⚠️  terminal-notifier found but Homebrew not available"
        fi
    else
        echo "✓ Keeping terminal-notifier"
    fi
fi

# 6. Instructions for manual cleanup
echo ""
echo "Manual cleanup required:"
echo "========================"
echo ""
echo "1. macOS Shortcut:"
echo "   - Open Shortcuts app"
echo "   - Find 'Edit with Claude' and delete it"
echo ""
echo "2. Keyboard Shortcut:"
echo "   - System Settings → Keyboard → Keyboard Shortcuts → Services"
echo "   - Find 'Edit with Claude' and remove the shortcut"
echo ""
echo "3. If you cloned the repository, you may want to delete it:"
echo "   - cd to parent directory and run: rm -rf claude-text-editor"
echo ""

echo "✅ Claude Text Editor has been uninstalled!"
echo ""
echo "Thank you for using Claude Text Editor!"