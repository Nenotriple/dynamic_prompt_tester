"""This module contains the InterfaceActions class, which is responsible for handling the GUI events for the Prompt Saver interface."""


from tkinter import messagebox


class InterfaceActions:
    def __init__(self, root, tester_ui):
        self.root = root
        self.tester_ui = tester_ui
        self.tree = None
        self.text_widget = None
        self.tree_manager = None
        self.status_bar = None


    def initialize(self, tree, text_widget, tree_manager, status_bar):
        self.tree = tree
        self.text_widget = text_widget
        self.tree_manager = tree_manager
        self.status_bar = status_bar
        self.tree_manager.auto_load_file(silent=True)


    def update_status_bar(self):
        selected = self.tree.selection()
        if not selected:
            folder_path = "/"
            folder_id = ""
        else:
            folder_id = selected[0]
            folder_path = self.get_folder_path(folder_id)
        folders, items = self.count_folder_contents(folder_id)
        status_text = f"Path: {folder_path}\nFolders: {folders}, Items: {items}"
        self.status_bar.config(text=status_text)


    def get_folder_path(self, folder_id):
        if not folder_id:
            return "/"
        path_parts = []
        current = folder_id
        while current:
            path_parts.insert(0, self.tree.item(current)['text'])
            current = self.tree.parent(current)
        return "/" + "/".join(path_parts)


    def count_folder_contents(self, folder_id):
        folders = 0
        items = 0
        for child in self.tree.get_children(folder_id):
            if self.tree_manager._is_folder(child):
                folders += 1
            else:
                items += 1
        return folders, items


    def handle_tree_item_selection(self):
        selected = self.tree.selection()
        if not selected:
            self.text_widget.delete('1.0', "end")
            self.text_widget.config(state='disabled')
        else:
            item_id = selected[0]
            if self.tree_manager._is_item(item_id):
                self.text_widget.config(state='normal')
                self.text_widget.delete('1.0', "end")
                self.text_widget.insert('1.0', self.tree_manager.get_item_content(item_id))
            else:
                self.text_widget.delete('1.0', "end")
                self.text_widget.config(state='disabled')
        self.update_status_bar()


    def on_search_change(self, *args):
        search_term = self.search_var.get()
        self.tree.filter_items(search_term, self.tree_manager, self.search_in_filename_var.get(), self.search_in_prompt_var.get())


    def send_to_tester(self):
        if not self.text_widget:
            return
        content = self.text_widget.get('1.0', "end-1c").strip()
        if not content:
            messagebox.showwarning("Empty Prompt", "No prompt text to send!")
            return
        tester_input = self.tester_ui.ui.input_text
        tester_input.delete('1.0', "end")
        tester_input.insert('1.0', content)
        self.root.nametowidget('!notebook').select(0)
        self.tester_ui.process_text()


    def save_prompt_to_item(self):
        selected = self.tree.selection()
        if selected and self.tree_manager._is_item(selected[0]):
            content = self.text_widget.get('1.0', "end-1c")
            self.tree_manager.save_item_content(selected[0], content)
            self.tree_manager.save_to_json(self.tree_manager.current_file, silent=True)
            messagebox.showinfo("Success", "Content saved successfully!")


    def _handle_save_and_close(self):
        if not self.tree_manager.changes_made:
            return True

        response = messagebox.askyesnocancel("Save and Close", "Save changes before quitting?")
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            if self.tree_manager.current_file:
                self.tree_manager.save_to_json(self.tree_manager.current_file, silent=True)
            else:
                self.tree_manager.save_to_json()
        return True


    def on_close(self):
        confirm = self._handle_save_and_close()
        return confirm
