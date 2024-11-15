import tkinter as tk
from tkinter import font

class TrackChangeTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor with Track Changes")
        
        # Allow window resizing
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Set up text widget with scrollbar
        self.text = tk.Text(root, wrap='word', undo=True, width=80, height=25)
        self.text.pack(expand=True, fill='both')  # Expand to fill available space
        
        # Set default colors and font size
        self.default_font_size = 22
        self.dark_mode = True
        self.base_text_color = "white"
        self.text.config(fg=self.base_text_color)
        
        # Define tags for tracked changes and bracketed text
        self.text.tag_configure("added", foreground="green")
        self.text.tag_configure("deleted", overstrike=True, foreground="red")
        self.text.tag_configure("bracketed", foreground="grey")
        
        # Initialize track changes status
        self.track_changes_enabled = False
        
        # Bind events for key shortcuts and text editing
        self.text.bind("<KeyPress>", self.track_insertion)
        self.text.bind("<Delete>", self.track_deletion)
        self.text.bind("<BackSpace>", self.track_deletion)
        self.text.bind("<Control-z>", self.undo_action)
        self.text.bind("<Control-t>", self.toggle_track_changes)
        self.text.bind("<Control-plus>", self.increase_font_size)
        self.text.bind("<Control-minus>", self.decrease_font_size)
        self.text.bind("<Control-equal>", self.increase_font_size)  # For laptops where "+" is "Shift+="
        
        # Menu for toggle and font size controls
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
        self.menu.add_command(label="Toggle Track Changes", command=self.toggle_track_changes)
        self.menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        
        # Toolbar for additional controls
        toolbar = tk.Frame(root)
        toolbar.pack(fill=tk.X)
        
        # Button to enable/disable track changes
        self.track_changes_button = tk.Button(toolbar, text="Enable Track Changes", command=self.toggle_track_changes)
        self.track_changes_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Button to increase font size
        increase_font_button = tk.Button(toolbar, text="Increase Font Size", command=self.increase_font_size)
        increase_font_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Set initial font
        self.current_font = font.Font(family="Helvetica", size=self.default_font_size)
        self.text.configure(font=self.current_font)
        
        # Apply bracketed color at startup
        self.apply_bracketed_color()
        
    def track_insertion(self, event):
        """Tracks insertion of new text by tagging it as 'added'."""
        if self.track_changes_enabled and len(event.char) == 1:
            # Check if there's a selection to overwrite
            if self.text.tag_ranges(tk.SEL):
                # Delete the selected text as a single action
                self.track_selection_as_deletion()
                
            current_index = self.text.index(tk.INSERT)
            # Insert the character manually to apply a tag
            self.text.insert(current_index, event.char)
            self.text.tag_add("added", current_index, f"{current_index} + 1 chars")
            self.text.edit_separator()  # Mark this point for undo history
            self.apply_bracketed_color()  # Re-apply bracketed text color
            return "break"  # Prevent the default insertion

    def track_deletion(self, event):
        """Tracks deletion by marking text as 'deleted'."""
        if not self.track_changes_enabled:
            return  # Skip if track changes is disabled

        if self.text.tag_ranges(tk.SEL):
            # If there’s a selection, delete it as a single action
            self.track_selection_as_deletion()
            return "break"  # Prevent default deletion behavior

        # Single character deletion
        if event.keysym == "BackSpace":
            start_index = self.text.index(f"{tk.INSERT} - 1 chars")
        else:
            start_index = self.text.index(tk.INSERT)

        end_index = self.text.index(f"{start_index} + 1 chars")
        deleted_text = self.text.get(start_index, end_index)
        
        if deleted_text:
            # Remove text and reinsert with 'deleted' tag
            self.text.delete(start_index, end_index)
            self.text.insert(start_index, deleted_text, "deleted")
            self.text.edit_separator()  # Mark this point for undo history
            if event.keysym == "BackSpace":
                self.text.mark_set(tk.INSERT, start_index)
            self.apply_bracketed_color()  # Re-apply bracketed text color
        return "break"
    
    def track_selection_as_deletion(self):
        """Handles deleting the selected text as a single 'deleted' action."""
        start_index = self.text.index(tk.SEL_FIRST)
        end_index = self.text.index(tk.SEL_LAST)
        selected_text = self.text.get(start_index, end_index)
        
        # Delete the selected text and reinsert with the 'deleted' tag
        self.text.delete(start_index, end_index)
        self.text.insert(start_index, selected_text, "deleted")
        self.text.tag_remove(tk.SEL, "1.0", tk.END)  # Deselect text
        self.text.mark_set(tk.INSERT, start_index)
        self.text.edit_separator()  # Mark this point for undo history
        self.apply_bracketed_color()  # Re-apply bracketed text color
    
    def toggle_track_changes(self, event=None):
        """Toggle the track changes feature."""
        self.track_changes_enabled = not self.track_changes_enabled
        if self.track_changes_enabled:
            self.track_changes_button.config(text="Disable Track Changes")
        else:
            self.track_changes_button.config(text="Enable Track Changes")
        return "break"  # Prevent default behavior for Ctrl+T
    
    def toggle_dark_mode(self):
        """Toggle dark mode and set appropriate text color."""
        self.dark_mode = not self.dark_mode
        self.base_text_color = "white" if self.dark_mode else "black"
        self.text.config(bg="black" if self.dark_mode else "white", fg=self.base_text_color)
        self.apply_bracketed_color()  # Update bracketed text color

    def increase_font_size(self, event=None):
        """Increases the font size in the text widget without resizing the window."""
        self.default_font_size += 2
        self.current_font.config(size=self.default_font_size)
        self.text.configure(font=self.current_font)
        self.apply_bracketed_color()  # Re-apply bracketed text color
        return "break"  # Prevent default behavior for Ctrl+Plus
    
    def decrease_font_size(self, event=None):
        """Decreases the font size in the text widget without resizing the window."""
        if self.default_font_size > 6:  # Set a minimum font size limit
            self.default_font_size -= 2
            self.current_font.config(size=self.default_font_size)
            self.text.configure(font=self.current_font)
            self.apply_bracketed_color()  # Re-apply bracketed text color
        return "break"  # Prevent default behavior for Ctrl+Minus
    
    def apply_bracketed_color(self):
        """Applies grey color to text within round brackets."""
        self.text.tag_remove("bracketed", "1.0", tk.END)  # Clear previous tags
        text_content = self.text.get("1.0", tk.END)
        start = 0
        
        while True:
            # Find the next open and close parentheses
            open_idx = text_content.find("(", start)
            close_idx = text_content.find(")", open_idx + 1)
            
            if open_idx == -1 or close_idx == -1:
                break  # No more brackets
            
            # Apply the "bracketed" tag
            start_index = f"1.0 + {open_idx} chars"
            end_index = f"1.0 + {close_idx + 1} chars"
            self.text.tag_add("bracketed", start_index, end_index)
            
            # Move to the next character after the close bracket
            start = close_idx + 1
    
    def undo_action(self, event=None):
        """Performs an undo operation."""
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass  # Ignore if there's nothing to undo
        return "break"  # Prevent default behavior for Ctrl+Z

# Main loop
root = tk.Tk()
app = TrackChangeTextEditor(root)
root.mainloop()

