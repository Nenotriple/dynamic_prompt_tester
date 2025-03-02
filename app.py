"""
Main entry point for the application.
This module creates the main window and the main application object.
It also creates the notebook and the tester app object.
The main application object is responsible for setting the random seed and processing the text input.
The tester app object is responsible for managing the wildcard manager, the text processor, and the Prompt Tester interface.
"""

# Standard Library - GUI
import tkinter as tk
from tkinter import ttk, Menu

# Local Imports
from help_text import HELP_TEXT
from tester.main import PromptTester
from saver.main import PromptSaver


# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 600
MIN_WINDOW_SIZE = (500, 375)


class HelpTab:
    def __init__(self, parent):
        self.parent = parent
        self.create_help_tab()


    def create_help_tab(self):
        help_frame = ttk.Frame(self.parent)
        help_frame.pack(fill="both", expand=True, padx=10, pady=10)
        help_text = tk.Text(help_frame, wrap="word", width=120, height=30)
        scrollbar = ttk.Scrollbar(help_frame, orient="vertical", command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        help_text.pack(side="left", fill="both", expand=True)
        help_text.insert("1.0", HELP_TEXT)
        help_text.config(state="disabled")


class MainApplication:
    def __init__(self):
        # Create window
        self.root = self._create_main_window()
        # Create notebook
        self.notebook, self.prompt_tester_tab, self.prompt_saver_tab, help_tab = self._create_notebook()
        # Create Prompt Tester, Prompt Saver, and Help UIs
        self.tester_ui = PromptTester(self.root, self.prompt_tester_tab)
        self.saver_ui = PromptSaver(self.root, self.prompt_saver_tab, self.tester_ui)
        self.help_tab = HelpTab(help_tab)
        # Create menubar and center window
        self._create_menubar()
        self._center_window()


    def _create_main_window(self):
        root = tk.Tk()
        root.title("Dynamic Prompt Tester")
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root.minsize(*MIN_WINDOW_SIZE)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        return root


    def _center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")


    def _create_menubar(self):
        menubar = Menu(self.root)
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Input/Output", command=self.tester_ui.ui.actions.clear_all_text)
        file_menu.add_command(label="Browse Wildcards Path...", command=self.tester_ui.ui.actions.browse_wildcards_path)
        file_menu.add_separator()
        file_menu.add_checkbutton(label="Toggle Always On Top", variable=self.tester_ui.ui.always_on_top_var, command=self.tester_ui.ui.toggle_always_on_top)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.root.config(menu=menubar)


    def _create_notebook(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)
        # Prompt Tester tab
        prompt_tester_tab = ttk.Frame(notebook)
        notebook.add(prompt_tester_tab, text="Prompt Tester")
        # Saved Prompts tab
        prompt_saver_tab = ttk.Frame(notebook)
        notebook.add(prompt_saver_tab, text="Saved Prompts")
        # Help tab
        help_tab = ttk.Frame(notebook)
        notebook.add(help_tab, text="Help")

        # Bind tab change event
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        return notebook, prompt_tester_tab, prompt_saver_tab, help_tab

    def _on_tab_changed(self, event):
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        if tab_text == "Saved Prompts":
            self.saver_ui.interface.tree_manager.load_from_json()


    def on_close(self):
        if self.saver_ui.actions.on_close():
            self.root.quit()
            self.root.destroy()


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainApplication()
    app.run()
