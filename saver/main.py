"""Main entry point for the Prompt Saver tab and interface."""

import tkinter as tk

from saver.interface import Interface
from saver.interface_actions import InterfaceActions


class PromptSaver:
    def __init__(self, root, tab, tester_ui):
        self.root = root
        self.tester_ui = tester_ui
        self.actions = InterfaceActions(root, tester_ui)
        self.interface = Interface(root, self, tab)
        # Initialize actions with UI components
        self.actions.initialize(
            # The custom TreeView widget, used to display the folders and prompts
            self.interface.tree,
            # The text widget, used to display and edit the prompt content
            self.interface.text_widget,
            # The TreeManager, used to manage the folder and prompt data
            self.interface.tree_manager,
            # The status bar, used to display the current folder path and item count
            self.interface.status_bar
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptSaver(root)
    root.mainloop()
