"""Create the Prompt Tester tab and interface."""

# Standard Library
import os

# Standard Library - GUI
from tkinter import ttk, Text, Menu
import tkinter as tk

# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip

# Local Imports
from tester.interface_actions import InterfaceActions


class Interface:
    def __init__(self, root, parent, tab):
        # Initialize
        self.root = root
        self.parent = parent
        self.prompt_tester_tab = tab
        self.wildcard_manager = parent.wildcard_manager
        self.process_text = parent.process_text
        # Variables
        self.live_var = tk.BooleanVar(value=True)
        self.fixed_seed_var = tk.BooleanVar(value=False)
        self.collapse_output_var = tk.BooleanVar(value=False)
        self.always_on_top_var = tk.BooleanVar(value=False)
        self.wildcard_path_var = tk.StringVar(value=self.wildcard_manager.wildcards_path)
        self.show_wildcards_var = tk.BooleanVar(value=True)
        self.wildcards_list = None
        # Actions handler
        self.actions = InterfaceActions(self, parent.wildcard_manager, parent.process_text)
        # Setup interface
        self.setup_interface()


    def is_fixed_seed(self):
        return self.fixed_seed_var.get()


# --------------------------------------
# Window
# --------------------------------------
    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top_var.get())


    def setup_interface(self):
        self.main_pane = ttk.Panedwindow(self.prompt_tester_tab, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True, side="left", padx=5)
        self.setup_text_widget_panes()
        self.setup_control_panel()


# --------------------------------------
# Control Panel
# --------------------------------------
    def setup_control_panel(self):
        control_frame = ttk.Frame(self.prompt_tester_tab)
        control_frame.pack(fill="y", side="left", padx=5)
        # Process button
        process_button = ttk.Button(control_frame, text="Process Text", command=self.process_text)
        process_button.pack(pady=(5, 0), fill="x")
        ToolTip.create(widget=process_button, text="Process Input Text", delay=250, padx=5, pady=5)
        self.save_prompt_button = ttk.Button(control_frame, text="Save Prompt", state="disabled")
        self.save_prompt_button.pack(pady=(0, 5), fill="x")
        ToolTip.create(widget=self.save_prompt_button, text="Save current prompt", delay=250, padx=5, pady=5)
        # Create notebook
        self.setup_control_notebook(control_frame)


    def setup_control_notebook(self, control_frame):
        control_notebook = ttk.Notebook(control_frame)
        control_notebook.pack(fill="both", expand=True)
        # Options tab
        options_tab = ttk.Frame(control_notebook, padding=(10, 5, 10, 5))
        control_notebook.add(options_tab, text="Options")
        self.setup_control_options(options_tab)
        # Wildcards tab
        wildcards_tab = ttk.Frame(control_notebook, padding=(10, 5, 10, 5))
        control_notebook.add(wildcards_tab, text="Wildcards")
        self.setup_wildcards_frame(wildcards_tab)
        # Saved prompts tab
        saved_prompts_tab = ttk.Frame(control_notebook, padding=(10, 5, 10, 5))
        control_notebook.add(saved_prompts_tab, text="Saved Prompts")
        self.setup_saved_prompts_frame(saved_prompts_tab)


    def setup_control_options(self, parent):
        # Live Mode
        live_check = ttk.Checkbutton(parent, text="Live Processing", variable=self.live_var)
        live_check.pack(pady=5, fill="x")
        ToolTip.create(widget=live_check, text="Update output as you type", delay=250, padx=5, pady=5)
        # Fixed Seed
        fixed_seed_check = ttk.Checkbutton(parent, text="Fixed Seed", variable=self.fixed_seed_var)
        fixed_seed_check.pack(pady=5, fill="x")
        ToolTip.create(widget=fixed_seed_check, text="Use fixed seed for consistent results", delay=250, padx=5, pady=5)
        # Collapse Output
        collapse_output_check = ttk.Checkbutton(parent, text="Collapse Output", variable=self.collapse_output_var, command=self.actions.on_text_change)
        collapse_output_check.pack(pady=5, fill="x")
        ToolTip.create(widget=collapse_output_check, text="Collapse output to single line. Convert newlines to spaces.", delay=250, padx=5, pady=5)


    def setup_wildcards_frame(self, parent):
        # Wildcards path config
        path_entry = ttk.Entry(parent, textvariable=self.wildcard_path_var)
        path_entry.pack(fill="x", pady=2)
        self.wildcard_path_tooltip = ToolTip.create(widget=path_entry, text="...", delay=100, pady=20, origin="widget")
        self.create_text_context_menu(path_entry)
        # Browse and Open
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=2)
        browse_button = ttk.Button(button_frame, text="Browse...", command=self.actions.browse_wildcards_path)
        browse_button.pack(side="left", fill="x", expand=True, padx=(0, 2))
        ToolTip.create(widget=browse_button, text="Select wildcards folder", delay=250, padx=5, pady=5)
        self.open_button = ttk.Button(button_frame, text="Open", command=self.actions.open_wildcards_path, width=8)
        self.open_button.pack(side="right", fill="x", padx=(2, 0))
        ToolTip.create(widget=self.open_button, text="Open wildcards folder", delay=250, padx=5, pady=5)
        self.actions.update_wildcard_open_button_state()
        # Show Wildcards and Refresh
        wildcard_options_frame = ttk.Frame(parent)
        wildcard_options_frame.pack(fill="x", pady=5)
        show_wildcards_check = ttk.Checkbutton(wildcard_options_frame, text="Show Wildcards", variable=self.show_wildcards_var, command=self.actions.toggle_wildcards_list)
        show_wildcards_check.pack(side="left", pady=5, fill="x")
        ToolTip.create(widget=show_wildcards_check, text="Show/Hide wildcards list", delay=250, padx=5, pady=5)
        refresh_button = ttk.Button(wildcard_options_frame, text="⟳", width=2, command=self.actions.refresh_wildcards)
        refresh_button.pack(side="right", fill="x", pady=5)
        ToolTip.create(widget=refresh_button, text="Refresh wildcards", delay=250, padx=5, pady=5)
        # Wildcards list
        self.wildcards_list = tk.Listbox(parent, height=6)
        self.wildcards_list.pack(fill="both", expand=True, pady=5)
        self.create_wildcards_context_menu(self.wildcards_list)
        self.wildcards_list.bind('<Double-Button-1>', self.actions.on_wildcard_double_click)
        self.actions.update_wildcards_list()


    def setup_saved_prompts_frame(self, parent):
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", pady=5)
        self.saved_prompts_search_var = tk.StringVar()
        self.search_bar = ttk.Entry(search_frame, textvariable=self.saved_prompts_search_var)
        self.search_bar.pack(side="left", fill="x", expand=True)
        self.search_bar.bind('<KeyRelease>', self.actions.filter_saved_prompts)
        self.search_option_menu = ttk.Menubutton(search_frame, text="Options")
        self.search_option_menu.pack(side="right")
        self.search_option_menu.menu = tk.Menu(self.search_option_menu, tearoff=0)
        self.search_option_menu["menu"] = self.search_option_menu.menu
        self.search_option_menu.menu.add_checkbutton(label="Search in Filename")
        self.search_option_menu.menu.add_checkbutton(label="Search in Prompt")
        self.search_option_menu.menu.add_separator()
        self.search_option_menu.menu.add_command(label="Show Help")
        # Saved prompts list
        self.saved_prompts_listbox = tk.Listbox(parent, height=6)
        self.saved_prompts_listbox.pack(fill="both", expand=True, pady=5)



# --------------------------------------
# Primary
# --------------------------------------
    def setup_text_widget_panes(self):
        text_pane = ttk.Panedwindow(self.main_pane, orient="vertical")
        self.main_pane.add(text_pane, weight=1)
        self.setup_input_text_widgets(text_pane)
        self.setup_output_text_widgets(text_pane)


    def setup_input_text_widgets(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Input", padding=(5, 5, 5, 5))
        self.input_text = Text(input_frame, wrap="word", undo=True, width=5, height=1)
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        self.input_text.config(yscrollcommand=input_scrollbar.set)
        self.input_text.pack(side="left", fill="both", expand=True)
        input_scrollbar.pack(side="right", fill="y")
        self.input_text.bind('<KeyRelease>', self.actions.on_text_change)
        self.create_text_context_menu(self.input_text)
        parent.add(input_frame, weight=1)


    def setup_output_text_widgets(self, parent):
        output_frame = ttk.LabelFrame(parent, text="Output", padding=(5, 5, 5, 5))
        text_container = ttk.Frame(output_frame)
        text_container.pack(side="left", fill="both", expand=True)
        self.output_text = Text(text_container, wrap="word", width=5, height=1)
        self.output_text.pack(fill="both", expand=True)
        self.stats_bar = ttk.Label(text_container, text="Characters: 0 | Words: 0 | Tokens: ~0", anchor="w")
        self.stats_bar.pack(fill="x", pady=(5, 0))
        ToolTip.create(widget=self.stats_bar, text="Character, word, and estimated token counts", delay=250, padx=5, pady=5)
        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=output_scrollbar.set)
        self.output_text.bind('<<Selection>>', self.actions.update_stats_on_selection)
        self.output_text.bind('<FocusOut>', lambda e: self.actions.update_stats_bar())
        self.create_text_context_menu(self.output_text)
        parent.add(output_frame, weight=1)


# --------------------------------------
# Context Menus
# --------------------------------------
    def create_text_context_menu(self, widget):
        context_menu = Menu(self.root, tearoff=0)

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
                if isinstance(widget, Text):
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
            self.actions.on_text_change()

        def paste_with_callback():
            widget.event_generate("<<Paste>>")
            self.actions.on_text_change()

        def show_context_menu(event):
            update_menu_state()
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"

        context_menu.add_command(label="Cut", command=cut_with_callback)
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=paste_with_callback)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: (widget.tag_add("sel", "1.0", "end") if isinstance(widget, Text) else widget.select_range(0, "end")))
        widget.bind("<Button-3>", show_context_menu)


    def create_wildcards_context_menu(self, widget):
        context_menu = Menu(self.root, tearoff=0)

        def copy_wildcard():
            if widget.curselection():
                selected = widget.get(widget.curselection())
                self.root.clipboard_clear()
                self.root.clipboard_append(f"__{selected}__")

        def insert_wildcard():
            if widget.curselection():
                selected = widget.get(widget.curselection())
                self.input_text.insert(tk.INSERT, f"__{selected}__")
                self.actions.on_text_change()

        def open_wildcard():
            if widget.curselection() and self.wildcard_manager.wildcards_path:
                selected = widget.get(widget.curselection())
                file_path = os.path.join(self.wildcard_manager.wildcards_path, f"{selected}.txt")
                if os.path.exists(file_path):
                    os.startfile(file_path)

        def update_menu_state():
            state = "normal" if widget.curselection() else "disabled"
            context_menu.entryconfig("Copy", state=state)
            context_menu.entryconfig("Insert Selection", state=state)
            context_menu.entryconfig("Open", state=state)

        def show_context_menu(event):
            update_menu_state()
            context_menu.tk_popup(event.x_root, event.y_root)
            return "break"

        context_menu.add_command(label="Open", command=open_wildcard)
        context_menu.add_separator()
        context_menu.add_command(label="Copy", command=copy_wildcard)
        context_menu.add_command(label="Insert Selection", command=insert_wildcard)
        widget.bind("<Button-3>", show_context_menu)
