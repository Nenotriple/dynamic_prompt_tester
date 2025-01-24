"""Create the Prompt Saver tab and interface."""


#region Imports
import tkinter as tk
from tkinter import ttk

from saver.tree_manager import TreeManager
from saver.custom_treeview import CustomTreeview


class Interface:
    def __init__(self, root, parent, tab):
        self.root = root
        self.tab = tab
        self.actions = parent.actions
        self.search_var = tk.StringVar()
        self.search_in_filename_var = tk.BooleanVar(value=True)
        self.search_in_prompt_var = tk.BooleanVar(value=True)
        self.setup_user_interface()


    def setup_user_interface(self):
        self.paned_window = tk.PanedWindow(self.tab, orient="horizontal", sashwidth=8, sashrelief="ridge")
        self.paned_window.pack(fill="both", expand=True)
        self.setup_tree_view()
        self.setup_text_widget()


    def setup_tree_view(self):
        self.left_frame = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(self.left_frame, minsize=300)
        self.left_frame.pack_propagate(False)
        # Add search frame
        self.search_frame = ttk.Frame(self.left_frame)
        self.search_frame.pack(fill="x", pady=(0, 5))
        self.search_var.trace_add('write', self.actions.on_search_change)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.create_text_context_menu(self.search_entry)
        self.search_option_menu = ttk.Menubutton(self.search_frame, text="Options")
        self.search_option_menu.pack(side="right")
        self.search_option_menu.menu = tk.Menu(self.search_option_menu, tearoff=0)
        self.search_option_menu["menu"] = self.search_option_menu.menu
        self.search_option_menu.menu.add_checkbutton(label="Search in Filename", variable=self.search_in_filename_var)
        self.search_option_menu.menu.add_checkbutton(label="Search in Prompt", variable=self.search_in_prompt_var)
        self.search_option_menu.menu.add_separator()
        self.search_option_menu.menu.add_command(label="Show Help")
        # Tree
        self.tree_frame = ttk.Frame(self.left_frame)
        self.tree_frame.pack(fill="both", expand=True)
        self.tree = CustomTreeview(self.tree_frame)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.selection_callback = self.actions.handle_tree_item_selection
        self.tree_manager = TreeManager(self.tree)
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.update_status = self.actions.update_status_bar
        self.tree.bind("<Control-x>", lambda e: self.tree_manager.cut_selected())
        self.tree.bind("<Control-c>", lambda e: self.tree_manager.copy_selected())
        self.tree.bind("<Control-v>", lambda e: self.tree_manager.paste_clipboard())
        self.tree.bind("<Delete>",  lambda e: self.tree_manager.delete_selected())
        # Button frame
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.pack(fill="x")
        # Add Menu
        self.add_menu_button = ttk.Menubutton(self.button_frame, text="New")
        self.add_menu_button.grid(row=0, column=0, sticky="ew")
        self.add_menu = tk.Menu(self.add_menu_button, tearoff=0)
        self.add_menu_button["menu"] = self.add_menu
        self.add_menu.add_command(label="New Folder", command=lambda: self.tree_manager._add_entry(is_folder=True))
        self.add_menu.add_command(label="New Prompt", command=lambda: self.tree_manager._add_entry(is_folder=False))
        # Edit Menu
        self.edit_menu_button = ttk.Menubutton(self.button_frame, text="Edit")
        self.edit_menu_button.grid(row=0, column=1, sticky="ew")
        self.edit_menu = tk.Menu(self.edit_menu_button, tearoff=0)
        self.edit_menu_button["menu"] = self.edit_menu
        self.edit_menu.add_command(label="Cut", command=self.tree_manager.cut_selected)
        self.edit_menu.add_command(label="Copy", command=self.tree_manager.copy_selected)
        self.edit_menu.add_command(label="Paste", command=self.tree_manager.paste_clipboard)
        self.edit_menu.add_command(label="Rename", command=self.tree_manager.edit_folder)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Delete", command=self.tree_manager.delete_selected)
        # File Menu
        self.file_menu_button = ttk.Menubutton(self.button_frame, text="File")
        self.file_menu_button.grid(row=0, column=2, sticky="ew")
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button["menu"] = self.file_menu
        self.file_menu.add_command(label="Save Tree", command=self.tree_manager.save_to_json)
        self.file_menu.add_command(label="Load Tree", command=self.tree_manager.load_from_json)
        # Configure grid
        for i in range(3):
            self.button_frame.columnconfigure(i, weight=1)


    def setup_text_widget(self):
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame)
        self.top_frame = ttk.Frame(self.right_frame)
        self.top_frame.pack(fill="x")
        # Status bar
        self.status_bar = ttk.Label(self.top_frame, text="Path: ...\nFolders: 0, Items: 0", anchor="w")
        self.status_bar.pack(side="left", fill="x")
        # Save prompt
        self.save_prompt_button = ttk.Button(self.top_frame, text="Save Prompt", command=self.actions.save_prompt_to_item)
        self.save_prompt_button.pack(side="right")
        self.send_to_tester_button = ttk.Button(self.top_frame, text="Send to Tester", command=self.actions.send_to_tester)
        self.send_to_tester_button.pack(side="right")
        # Text widget
        self.text_frame = ttk.Frame(self.right_frame)
        self.text_frame.pack(fill="both", expand=True)
        self.text_widget = tk.Text(self.text_frame, wrap="word", height=1)
        self.text_widget.pack(side="left", fill="both", expand=True)
        self.text_scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_scrollbar.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=self.text_scrollbar.set)
        self.create_text_context_menu(self.text_widget)


    def create_text_context_menu(self, widget):
        context_menu = tk.Menu(self.root, tearoff=0)

        def update_menu_state():
            check_for_selection()
            check_clipboard_content()

        def check_clipboard_content():
            try:
                clipboard = self.root.clipboard_get()
                if isinstance(clipboard, str):
                    context_menu.entryconfig("Paste", state="normal")
                else:
                    context_menu.entryconfig("Paste", state="disabled")
            except tk.TclError:
                context_menu.entryconfig("Paste", state="disabled")

        def check_for_selection():
            try:
                if isinstance(widget, tk.Text):
                    has_selection = widget.tag_ranges("sel")
                else:  # Entry widget
                    has_selection = widget.selection_present()

                state = "normal" if has_selection else "disabled"
                context_menu.entryconfig("Cut", state=state)
                context_menu.entryconfig("Copy", state=state)
            except tk.TclError:
                context_menu.entryconfig("Cut", state="disabled")
                context_menu.entryconfig("Copy", state="disabled")

        def cut_with_callback():
            widget.event_generate("<<Cut>>")

        def paste_with_callback():
            widget.event_generate("<<Paste>>")

        def show_context_menu(event):
            update_menu_state()
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"

        context_menu.add_command(label="Cut", command=cut_with_callback)
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=paste_with_callback)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: (widget.tag_add("sel", "1.0", "end") if isinstance(widget, tk.Text) else widget.select_range(0, "end")))
        widget.bind("<Button-3>", show_context_menu)
