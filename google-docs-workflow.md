# Claude Text Editor - Google Docs Workflow

Since Google Docs overrides system shortcuts and right-click menus, here are alternative workflows:

## Option 1: Copy-Paste Workflow (Simplest)

1. **Select text** in Google Docs
2. **Copy** with ⌘C
3. **Switch to any native app** (TextEdit, Notes, Terminal)
4. **Paste** and then use ⌥⌘. (our shortcut works here!)
5. **Copy result** and paste back to Google Docs

## Option 2: Use the Client Script Directly

1. **Select and copy text** in Google Docs (⌘C)
2. **Open Terminal**
3. **Run**: `pbpaste | ~/claude-text-editor/claude_text_client.py`
4. Result is automatically in clipboard
5. **Paste back** to Google Docs (⌘V)

## Option 3: Create a Quick Automator App

1. Open **Automator**
2. Create new **Quick Action**
3. Add **Run Shell Script** action:
   ```bash
   pbpaste | ~/claude-text-editor/claude_text_client.py
   ```
4. Save as "Edit with Claude (Clipboard)"
5. Assign a different shortcut like ⌃⌥⌘E

Now in Google Docs:
- Copy text (⌘C)
- Run shortcut (⌃⌥⌘E) 
- Paste result (⌘V)

## Option 4: Bookmarklet (For Quick Access)

Create a bookmark with this URL:
```javascript
javascript:(function(){
  const text = window.getSelection().toString();
  if(text) {
    navigator.clipboard.writeText(text).then(() => {
      alert('Text copied! Switch to a native app and use ⌥⌘. to edit with Claude');
    });
  }
})();
```

## Option 5: Browser Extension (Advanced)

We've created a browser extension in `browser-extension/` that:
- Captures Alt+Shift+E in Google Docs
- Copies selected text
- Shows notification to use ⌥⌘. in a native app

To install:
1. Open Chrome → Extensions → Manage Extensions
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `browser-extension` folder

## Recommended Workflow

For Google Docs, we recommend **Option 2** (Terminal workflow) because:
- It's reliable and always works
- No additional setup needed
- Fast once you get used to it

You can even create an alias in your `~/.zshrc`:
```bash
alias claude-edit='pbpaste | ~/claude-text-editor/claude_text_client.py'
```

Then just:
1. Copy in Google Docs
2. Type `claude-edit` in Terminal
3. Paste back in Google Docs