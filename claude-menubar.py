#!/usr/bin/env python3
"""
Claude Text Editor Menu Bar Helper
Provides easy access to text editing from the menu bar
"""

import subprocess
import sys
import os
from pathlib import Path

try:
    import rumps
except ImportError:
    print("Installing rumps (menu bar library)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rumps"])
    import rumps

class ClaudeMenuBarApp(rumps.App):
    def __init__(self):
        super(ClaudeMenuBarApp, self).__init__("Claude Editor", icon="📝")
        self.menu = [
            rumps.MenuItem("Edit Clipboard Text", callback=self.edit_clipboard),
            rumps.MenuItem("Edit Selected Text", callback=self.edit_selected),
            None,  # Separator
            rumps.MenuItem("Open Inbox Folder", callback=self.open_inbox),
            rumps.MenuItem("Open Outbox Folder", callback=self.open_outbox),
            None,  # Separator
            rumps.MenuItem("Settings", callback=self.open_settings),
        ]
    
    @rumps.clicked("Edit Clipboard Text")
    def edit_clipboard(self, _):
        """Edit text currently in clipboard"""
        try:
            # Get clipboard content
            clipboard_text = subprocess.check_output(['pbpaste'], text=True)
            
            if not clipboard_text.strip():
                rumps.notification("Claude Text Editor", "No text in clipboard", "Copy some text first")
                return
            
            # Process with claude_text_client
            client_path = Path.home() / "claude-text-editor" / "claude_text_client.py"
            if not client_path.exists():
                rumps.notification("Claude Text Editor", "Error", "Client not found. Please run install.sh")
                return
            
            # Run the client
            process = subprocess.Popen(
                [str(client_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=clipboard_text)
            
            if process.returncode == 0:
                # Result is already in clipboard
                rumps.notification("Claude Text Editor", "Success!", "Edited text copied to clipboard")
            else:
                rumps.notification("Claude Text Editor", "Error", "Failed to process text")
        
        except Exception as e:
            rumps.notification("Claude Text Editor", "Error", str(e))
    
    @rumps.clicked("Edit Selected Text")
    def edit_selected(self, _):
        """Tell user to copy first for web apps"""
        rumps.notification(
            "Claude Text Editor",
            "For Web Apps (Google Docs, etc.)",
            "1. Copy text (⌘C)\n2. Click 'Edit Clipboard Text'\n3. Paste result (⌘V)"
        )
    
    @rumps.clicked("Open Inbox Folder")
    def open_inbox(self, _):
        inbox = Path.home() / ".claude_text_editor" / "inbox"
        subprocess.run(["open", str(inbox)])
    
    @rumps.clicked("Open Outbox Folder")  
    def open_outbox(self, _):
        outbox = Path.home() / ".claude_text_editor" / "outbox"
        subprocess.run(["open", str(outbox)])
    
    @rumps.clicked("Settings")
    def open_settings(self, _):
        prompt_file = Path.home() / ".claude_text_editor" / "claude_prompt.txt"
        subprocess.run(["open", str(prompt_file)])

if __name__ == "__main__":
    app = ClaudeMenuBarApp()
    app.run()