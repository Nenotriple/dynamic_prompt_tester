"""This module contains the InterfaceActions class, which is responsible for handling the GUI events for the Prompt Tester interface."""

# Standard Library
import os
import re
import json


# Standard Library - GUI
from tkinter import filedialog, simpledialog
import tkinter as tk


class InterfaceActions:
    def __init__(self, interface, wildcard_manager, process_callback):
        self.interface = interface
        self.wildcard_manager = wildcard_manager
        self.process_text_callback = process_callback
        self.saved_prompts_dict = {}
        self.json_path = "config\\prompts.json"


    def on_text_change(self, event=None):
        if self.interface.live_var.get():
            self.process_text_callback()
        self.update_save_button_state()


    def display_text_output(self, text):
        if self.interface.collapse_output_var.get():
            text = ' '.join(text.split())
        self.interface.output_text.delete("1.0", "end")
        self.interface.output_text.insert("end", text)
        self.update_stats_bar(text)


    def get_input_text(self):
        text = self.interface.input_text.get("1.0", "end").strip()
        lines = [line for line in text.splitlines() if not line.strip().startswith('#')]
        return re.sub(r'\n\s*\n', '\n\n', '\n'.join(lines))


    def clear_all_text(self):
        self.interface.input_text.delete("1.0", "end")
        self.interface.output_text.delete("1.0", "end")
        self.update_stats_bar("")


    def browse_wildcards_path(self):
        path = filedialog.askdirectory(title="Select Wildcards Folder", initialdir=os.getcwd())
        if path:
            self.wildcard_manager.set_wildcards_path(path)
            self.interface.wildcard_path_var.set(path)
            self.update_wildcard_open_button_state()
            self.interface.wildcard_path_tooltip.config(text=path)
            if self.interface.show_wildcards_var.get():
                self.update_wildcards_list()


    def toggle_wildcards_list(self):
        if self.interface.show_wildcards_var.get():
            self.update_wildcards_list()
            self.interface.wildcards_list.pack(fill="both", expand=True, pady=5)
        else:
            self.interface.wildcards_list.pack_forget()


    def update_wildcards_list(self):
        if self.wildcard_manager.wildcards_path:
            self.interface.wildcards_list.delete(0, "end")
            for wildcard in self.wildcard_manager.get_available_wildcards():
                self.interface.wildcards_list.insert("end", wildcard)
            self.interface.wildcard_path_tooltip.config(text=self.wildcard_manager.wildcards_path)


    def on_wildcard_double_click(self, event):
        if self.interface.wildcards_list.curselection():
            selected = self.interface.wildcards_list.get(self.interface.wildcards_list.curselection())
            self.interface.input_text.insert(tk.INSERT, f"__{selected}__")
            self.on_text_change()


    def update_wildcard_open_button_state(self):
        state = "normal" if self.wildcard_manager.wildcards_path else "disabled"
        self.interface.open_button.configure(state=state)


    def open_wildcards_path(self):
        if self.wildcard_manager.wildcards_path:
            os.startfile(self.wildcard_manager.wildcards_path)


    def refresh_wildcards(self):
        self.wildcard_manager.reload_wildcards()
        self.update_wildcards_list()


    def estimate_token_count(self, text):
        words = text.split()
        token_count = 0
        for word in words:
            punctuation_count = sum(1 for char in word if char in '.,!?;:()[]{}"\'')
            if len(word) > 8:
                token_count += max(2, len(word) // 4)
            else:
                token_count += 1
            token_count += punctuation_count
        return max(1, token_count)


    def calculate_text_stats(self, text):
        char_count = len(text)
        word_count = len(text.split())
        token_count = self.estimate_token_count(text)
        return f"Characters: {char_count} | Words: {word_count} | Tokens: ~{token_count}"


    def update_stats_bar(self, text=None):
        if text is None:
            text = self.interface.output_text.get("1.0", "end").strip()
        self.interface.stats_bar.config(text=self.calculate_text_stats(text))


    def update_stats_on_selection(self, event=None):
        try:
            selected_text = self.interface.output_text.get("sel.first", "sel.last")
            self.update_stats_bar(selected_text)
        except tk.TclError:  # No selection
            self.update_stats_bar()


    def update_save_button_state(self):
        if self.interface.input_text.get("1.0", "end").strip():
            self.interface.save_prompt_button.configure(state="normal")
        else:
            self.interface.save_prompt_button.configure(state="disabled")


    def filter_saved_prompts(self, event=None):
        search_term = self.interface.saved_prompts_search_var.get().lower()
        selected_folder = self.interface.prompt_folder_combo.get()
        search_filename = self.interface.search_in_filename_var.get()
        search_prompt = self.interface.search_in_prompt_var.get()
        # Get prompts from selected folder
        prompts = self.get_prompts_from_folder(selected_folder)
        # Clear the listbox
        self.interface.saved_prompts_listbox.delete(0, tk.END)
        # Filter and insert matching prompts
        for prompt in prompts:
            matches = False
            if not search_term:
                matches = True
            else:
                if search_filename and search_term in prompt.lower():
                    matches = True
                if search_prompt and prompt in self.saved_prompts_dict:
                    content = self.saved_prompts_dict[prompt].get('content', '').lower()
                    if search_term in content:
                        matches = True
            if matches:
                self.interface.saved_prompts_listbox.insert(tk.END, prompt)


    def load_json(self):
        if not self.json_path or not os.path.exists(self.json_path):
            return {}
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return {}

    def save_json(self, data):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving JSON file: {e}")


    def get_json_folders_dict(self, include_children=False):
        """Returns a dictionary of folder names and their contents from the 'prompts.json' file.

        Args:
            include_children (bool): If True, includes the children items in the result

        Returns:
            dict: Dictionary of folder names and their IDs, with optional children content
        """
        data = self.load_json()
        if not data:
            return {}

        def process_items(items, current_path="", folders=None):
            if folders is None:
                folders = {}
            for item in items:
                if item['type'] == 'folder':
                    new_path = f"{current_path}/{item['text']}" if current_path else item['text']
                    folders[new_path] = {
                        'name': item['text'],
                        'id': item.get('id', '')
                    }
                    if include_children:
                        folders[new_path]['children'] = item.get('children', [])
                    if 'children' in item:
                        process_items(item['children'], new_path, folders)
            return folders
        return process_items(data['items'] if isinstance(data, dict) else data)


    def get_prompts_from_folder(self, folder_path=None):
        """Get prompt items from a specific folder in the JSON structure."""
        data = self.load_json()
        if not data:
            return []
        try:
            items = data['items'] if isinstance(data, dict) else data

            def collect_items_from_path(items, target_path=None, current_path=""):
                prompts = []
                for item in items:
                    if item['type'] == 'item':
                        # For root items or when we want all items
                        if target_path is None or (target_path == "/" and current_path == ""):
                            prompts.append(item['text'])
                        # For items in a specific folder
                        elif current_path == target_path:
                            prompts.append(item['text'])
                    elif item['type'] == 'folder' and 'children' in item:
                        new_path = f"{current_path}/{item['text']}" if current_path else item['text']
                        prompts.extend(collect_items_from_path(item['children'], target_path, new_path))
                return prompts

            # Handle different folder selection cases
            if folder_path == "ALL" or not folder_path:
                return sorted(collect_items_from_path(items), key=str.lower)
            elif folder_path == "/":
                return sorted(collect_items_from_path(items, "/"), key=str.lower)
            else:
                return sorted(collect_items_from_path(items, folder_path), key=str.lower)
        except Exception as e:
            print(f"Error getting prompts from folder: {e}")
            return []


    def populate_prompt_folder_combo(self):
        folders = self.get_json_folders_dict()
        folder_names = list(folders.keys())
        self.interface.prompt_folder_combo["values"] = ["ALL", "/"] + folder_names


    def populate_saved_prompts_list(self):
        """Populates the saved prompts listbox with items from prompts.json"""
        data = self.load_json()
        if not data:
            return
        try:
            def collect_items(items):
                prompt_items = []
                for item in items:
                    if item['type'] == 'item':
                        # Store all item data in dictionary
                        self.saved_prompts_dict[item['text']] = {
                            'id': item.get('id', ''),
                            'text': item['text'],
                            'content': item.get('content', '')
                        }
                        prompt_items.append(item['text'])
                    elif item['type'] == 'folder' and 'children' in item:
                        prompt_items.extend(collect_items(item['children']))
                return prompt_items

            # Clear existing items and dictionary
            self.interface.saved_prompts_listbox.delete(0, tk.END)
            self.saved_prompts_dict.clear()
            # Get all prompt titles and sort them
            prompts = collect_items(data['items'] if isinstance(data, dict) else data)
            prompts.sort(key=str.lower)
            # Insert into listbox
            for prompt in prompts:
                self.interface.saved_prompts_listbox.insert(tk.END, prompt)
        except Exception as e:
            print(f"Error populating saved prompts list: {e}")


    def on_prompt_select(self, event=None):
        """Handles the selection of a prompt in the saved_prompts_listbox widget"""
        selection = self.interface.saved_prompts_listbox.curselection()
        if not selection:
            return
        self.refresh_json_data()
        selected_text = self.interface.saved_prompts_listbox.get(selection[0])
        prompt_data = self.saved_prompts_dict.get(selected_text)
        if prompt_data and prompt_data.get('content'):
            # Clear current input and insert new content
            self.interface.input_text.delete("1.0", tk.END)
            self.interface.input_text.insert("1.0", prompt_data['content'])
            self.on_text_change()


    def refresh_json_data(self):
        """Refreshes the JSON data and updates related widgets."""
        try:
            # Refresh folder combo
            self.populate_prompt_folder_combo()
            # Refresh saved prompts list and dictionary
            self.populate_saved_prompts_list()
            # Reapply current filters
            self.filter_saved_prompts()
        except Exception as e:
            print(f"Error refreshing JSON data: {e}")


    def _find_folder_in_json(self, items, folder_id):
        """Helper function to find a folder in JSON structure by ID"""
        for item in items:
            if item.get('id') == folder_id and item.get('type') == 'folder':
                return item
            if item.get('type') == 'folder' and 'children' in item:
                found = self._find_folder_in_json(item['children'], folder_id)
                if found:
                    return found
        return None


    def save_prompt_to_folder(self, folder_id, prompt_title, prompt_content):
        """
        Save a prompt to a specific folder in the JSON file directly.

        Args:
            folder_id: The ID of the folder where the prompt should be saved
            prompt_title: The title of the prompt
            prompt_content: The content of the prompt

        Returns:
            str: The ID of the newly created prompt item, or None if failed
        """
        data = self.load_json()
        if not data:
            return None
        try:
            if folder_id == "ROOT":
                # Generate a unique ID
                existing_ids = []

                def collect_ids(items):
                    for item in items:
                        existing_ids.append(item.get('id', ''))
                        if item.get('type') == 'folder' and 'children' in item:
                            collect_ids(item['children'])
                collect_ids(data['items'])

                new_id = 'I000'
                counter = 0
                while new_id in existing_ids:
                    counter += 1
                    new_id = f'I{counter:03X}'
                # Create new prompt entry
                new_prompt = {
                    "text": prompt_title,
                    "type": "item",
                    "id": new_id,
                    "content": prompt_content
                }
                data['items'].append(new_prompt)
                # Save back to file
                self.save_json(data)
                return new_id
            folder = self._find_folder_in_json(data['items'], folder_id)
            if not folder:
                return None
            # Generate a unique ID
            existing_ids = []

            def collect_ids(items):
                for item in items:
                    existing_ids.append(item.get('id', ''))
                    if item.get('type') == 'folder' and 'children' in item:
                        collect_ids(item['children'])
            collect_ids(data['items'])

            new_id = 'I000'
            counter = 0
            while new_id in existing_ids:
                counter += 1
                new_id = f'I{counter:03X}'
            # Create new prompt entry
            new_prompt = {
                "text": prompt_title,
                "type": "item",
                "id": new_id,
                "content": prompt_content
            }
            # Add to folder's children
            if 'children' not in folder:
                folder['children'] = []
            folder['children'].append(new_prompt)
            # Save back to file
            self.save_json(data)
            return new_id
        except Exception as e:
            print(f"Error saving prompt to folder: {str(e)}")
            return None

    def on_save_prompt(self):
        text = self.get_input_text()
        if not text:
            return
        prompt_title = simpledialog.askstring("Save Prompt", "Enter a title for your prompt:")
        if not prompt_title:
            return
        folder_name = self.interface.prompt_folder_combo.get()
        folder_id = self._get_folder_id_by_name(folder_name)
        saved_id = self.save_prompt_to_folder(folder_id, prompt_title, text)
        if saved_id:
            self.refresh_json_data()

    def _get_folder_id_by_name(self, folder_name):
        if folder_name in ("ALL", "/"):
            return "ROOT"
        folders = self.get_json_folders_dict()
        folder_data = folders.get(folder_name)
        return folder_data['id'] if folder_data else None