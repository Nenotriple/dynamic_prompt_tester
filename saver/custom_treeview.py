"""Custom Treeview widget for the folder tree view."""


from tkinter import ttk, messagebox

from PIL import Image, ImageTk


class CustomTreeview(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.editing_item = None
        self.editor = None
        self.hidden_items = set()
        self.search_term = ""
        self._init_ui()


    def _init_ui(self):
        self.heading('#0', text='Folders and Prompts', anchor="w")
        self.setup_event_handlers()
        self.load_icons()


    def setup_event_handlers(self):
        events = {
            '<<TreeviewSelect>>': self._handle_selection,
            '<Button-1>': lambda e: self.selection_remove(self.selection()) if self.identify_region(e.x, e.y) == "heading" else None,
            '<Double-1>': self.start_editing,
        }
        for event, handler in events.items():
            self.bind(event, handler)


    def load_icons(self):
        try:
            for icon_name in ['folder', 'file']:
                with Image.open(f"saver\\{icon_name}.png") as icon:
                    icon.thumbnail((16, 16))
                    setattr(self, f"{icon_name}_icon", ImageTk.PhotoImage(icon))
                    self.tag_configure(icon_name if icon_name == 'folder' else 'item', image=getattr(self, f"{icon_name}_icon"))
        except Exception as e:
            messagebox.showerror("ERROR - load_icons()", f"Failed to load icons: {str(e)}")


    def _handle_selection(self, event):
        if hasattr(self, 'selection_callback'):
            self.selection_callback()


    def start_editing(self, event):
        item = self.identify_row(event.y)
        if not item or not (bbox := self.bbox(item)):
            return
        self.editing_item = item
        self.editor = ttk.Entry(self)
        self.editor.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.editor.insert(0, self.item(item)['text'])
        self.editor.select_range(0, 'end')
        self.editor.focus_set()
        # Bind editor events
        for event, handler in {
            '<Return>': self._complete_editing,
            '<Escape>': self._cleanup_editor,
            '<FocusOut>': self._cleanup_editor
        }.items():
            self.editor.bind(event, handler)


    def _complete_editing(self, event=None):
        if not self.editor:
            return
        new_text = self.editor.get()
        item = self.editing_item
        self._cleanup_editor()
        if new_text:
            self.item(item, text=new_text)
            if hasattr(self, 'sort_callback'):
                self.sort_callback(self.parent(item))
            if hasattr(self, 'update_status'):
                self.update_status()


    def _cleanup_editor(self, event=None):
        if self.editor:
            self.editor.destroy()
            self.editor = None
            self.editing_item = None


    def filter_items(self, search_term, tree_manager, search_in_filename=True, search_in_prompt=True):
        self.search_term = search_term.lower()
        # Reset visibility
        for item in self.hidden_items:
            self.reattach(item, self.parent(item), self.index(item))
        self.hidden_items.clear()
        if not search_term:
            return
        # Split search terms by + and remove empty terms
        search_terms = [term.strip() for term in self.search_term.split('+') if term.strip()]

        def matches_search(item_id):
            text = self.item(item_id)['text'].lower()
            content = tree_manager.get_item_content(item_id).lower() if tree_manager._is_item(item_id) else ""
            # Check each search term (OR operation)
            for term in search_terms:
                if (search_in_filename and term in text) or \
                   (search_in_prompt and tree_manager._is_item(item_id) and term in content):
                    return True
            return False

        def process_tree(node):
            # Process all children of the current node
            children = self.get_children(node)
            visible = any(matches_search(child) or
                        (tree_manager._is_folder(child) and process_tree(child))
                        for child in children)
            # Hide non-matching items
            for child in children:
                if not (matches_search(child) or
                       (tree_manager._is_folder(child) and visible)):
                    self.detach(child)
                    self.hidden_items.add(child)
            # Hide empty folders except root
            if not visible and not matches_search(node) and node != '':
                self.detach(node)
                self.hidden_items.add(node)
            return visible

        process_tree('')
