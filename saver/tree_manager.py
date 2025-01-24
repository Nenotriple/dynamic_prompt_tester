"""This module contains the TreeManager class, which is responsible for managing the custom treeview widget."""


import os
import json
from tkinter import messagebox, simpledialog, filedialog


class TreeManager:
    def __init__(self, tree):
        self.tree = tree
        self.tree.sort_callback = self.sort_treeview
        self.items_content = {}
        self.current_file = None
        self.default_file = "config\\prompts.json"
        self.last_selected = None
        self.saved_search_term = None
        self.clipboard = None
        self.changes_made = False


    def _is_folder(self, item_id):
        return 'folder' in self.tree.item(item_id, 'tags')


    def _is_item(self, item_id):
        return 'item' in self.tree.item(item_id, 'tags')


    def sort_treeview(self, parent=''):
        # Get all items under the parent
        items = self.tree.get_children(parent)
        if not items:
            return
        # Separate folders and regular items
        folders = [i for i in items if self._is_folder(i)]
        regular_items = [i for i in items if self._is_item(i)]
        # Sort folders and items separately by text
        folders.sort(key=lambda x: self.tree.item(x)['text'].lower())
        regular_items.sort(key=lambda x: self.tree.item(x)['text'].lower())
        # Move items in sorted order
        for i, item in enumerate(folders + regular_items):
            self.tree.move(item, parent, i)
            # Recursively sort children if it's a folder
            if self._is_folder(item):
                self.sort_treeview(item)


    def create_tree_entry(self, parent, text, entry_type='item', content=""):
        is_folder = entry_type == 'folder'
        entry_id = self.tree.insert(parent, 'end', text=text, tags=(entry_type,))
        if not is_folder:
            self.items_content[entry_id] = content
        self.sort_treeview(parent)
        self.tree.see(entry_id)
        self.tree.selection_set(entry_id)
        if hasattr(self.tree, 'update_status'):
            self.tree.update_status()
        self.changes_made = True
        return entry_id


    def edit_folder(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a folder or item to edit.")
            return
        item_id = selected_item[0]
        current_text = self.tree.item(item_id, 'text')
        new_text = simpledialog.askstring("Edit Name", "Enter new name:", initialvalue=current_text)
        if new_text:
            self.changes_made = True
            self.tree.item(item_id, text=new_text)
            parent = self.tree.parent(item_id)
            self.sort_treeview(parent)
            self.tree.update_status()


    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select folders or items to delete.")
            return
        if len(selected_items) > 1:
            if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_items)} items?"):
                return
        for item_id in selected_items:
            if item_id in self.items_content:
                del self.items_content[item_id]
            self.tree.delete(item_id)
            self.changes_made = True
        if hasattr(self.tree, 'update_status'):
            self.tree.update_status()


    def _add_entry(self, is_folder):
        selected_item = self.tree.selection()
        parent_id = selected_item[0] if selected_item else ''
        if selected_item and self._is_item(selected_item[0]):
            parent_id = self.tree.parent(selected_item[0])
        new_name = self._get_unique_name(parent_id, "New folder" if is_folder else "New prompt")
        return self.create_tree_entry(parent_id, new_name, 'folder' if is_folder else 'item')


    def _get_unique_name(self, parent_id, base_name):
        existing_items = [self.tree.item(item)['text'] for item in self.tree.get_children(parent_id)]
        if base_name not in existing_items:
            return base_name
        counter = 1
        while f"{base_name} ({counter})" in existing_items:
            counter += 1
        return f"{base_name} ({counter})"


    def get_item_content(self, item_id):
        return self.items_content.get(item_id, "")


    def save_item_content(self, item_id, content):
        if self.items_content.get(item_id) != content:
            self.changes_made = True
            self.items_content[item_id] = content


    def _temp_clear_filter(self):
        if hasattr(self.tree, 'search_term') and self.tree.search_term:
            self.saved_search_term = self.tree.search_term
            self.tree.filter_items("", self)
        else:
            self.saved_search_term = None


    def _restore_filter(self):
        if self.saved_search_term:
            self.tree.filter_items(self.saved_search_term, self)
            self.saved_search_term = None


    def copy_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select folders or items to copy.")
            return
        self.clipboard = []
        for item_id in selected_items:
            self.clipboard.append(self._copy_item_data(item_id))


    def _copy_item_data(self, item_id):
        item_data = {
            'text': self.tree.item(item_id)['text'],
            'type': 'folder' if self._is_folder(item_id) else 'item'
        }
        if item_data['type'] == 'folder':
            item_data['children'] = []
            for child in self.tree.get_children(item_id):
                item_data['children'].append(self._copy_item_data(child))
        else:
            item_data['content'] = self.items_content.get(item_id, '')
        return item_data


    def paste_clipboard(self):
        if not self.clipboard:
            messagebox.showwarning("Empty Clipboard", "Nothing to paste.")
            return
        selected_item = self.tree.selection()
        parent_id = selected_item[0] if selected_item else ''
        if selected_item and self._is_item(selected_item[0]):
            parent_id = self.tree.parent(selected_item[0])
        items_to_paste = self.clipboard if isinstance(self.clipboard, list) else [self.clipboard]
        for item_data in items_to_paste:
            base_name = item_data['text']
            new_name = self._get_unique_name(parent_id, base_name)
            self._paste_item_data(item_data, parent_id, new_name)
        self.sort_treeview(parent_id)
        if hasattr(self.tree, 'update_status'):
            self.tree.update_status()


    def _paste_item_data(self, item_data, parent_id, name):
        if item_data['type'] == 'folder':
            folder_id = self.create_tree_entry(parent_id, name, 'folder')
            for child in item_data['children']:
                child_name = self._get_unique_name(folder_id, child['text'])
                self._paste_item_data(child, folder_id, child_name)
        else:
            self.create_tree_entry(parent_id, name, 'item', item_data['content'])


    def cut_selected(self):
        self.copy_selected()
        self.delete_selected()


    def save_to_json(self, filepath=None, silent=False):
        self._temp_clear_filter()
        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not filepath:
            self._restore_filter()
            return
        tree_data = self._serialize_tree()
        try:
            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(tree_data, f, indent=2)
            self.current_file = filepath
            self.changes_made = False
            if not silent:
                messagebox.showinfo("Success", "Tree saved successfully!")
        except Exception as e:
            messagebox.showerror("ERROR - save_to_json()", f"Failed to save file: {str(e)}")
        finally:
            self._restore_filter()


    def load_from_json(self, filepath=None, silent=False):
        if not filepath:
            filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding="utf-8") as f:
                tree_data = json.load(f)
            self.tree.delete(*self.tree.get_children())
            self.items_content.clear()
            self._deserialize_tree(tree_data)
            self.current_file = filepath
            self.changes_made = False
            if not silent:
                messagebox.showinfo("Success", "Tree loaded successfully!")
        except Exception as e:
            messagebox.showerror("ERROR - load_from_json()", f"Failed to load file: {str(e)}")


    def auto_load_file(self, silent=False):
        if os.path.exists(self.default_file):
            self.load_from_json(self.default_file, silent=True)


    def _serialize_tree(self, parent=''):
        selected = self.tree.selection()
        result = {
            'items': [],
            'selected': selected[0] if selected else None
        }
        for item in self.tree.get_children(parent):
            item_data = {
                'text': self.tree.item(item)['text'],
                'type': 'folder' if self._is_folder(item) else 'item',
                'id': item
            }
            if item_data['type'] == 'folder':
                item_data['open'] = bool(self.tree.item(item)['open'])
                child_data = self._serialize_tree(item)
                item_data['children'] = child_data['items']
                if child_data.get('selected'):
                    result['selected'] = child_data['selected']
            else:
                item_data['content'] = self.items_content.get(item, '')
            result['items'].append(item_data)
        return result


    def _deserialize_tree(self, data, parent=''):
        items_data = data if isinstance(data, list) else data['items']
        selected_id = data.get('selected') if isinstance(data, dict) else None
        for item in items_data:
            if item['type'] == 'folder':
                folder_id = self.create_tree_entry(parent, item['text'], 'folder')
                child_data = {'items': item['children'], 'selected': selected_id}
                self._deserialize_tree(child_data, folder_id)
                self.tree.item(folder_id, open=item.get('open', False))
            else:
                item_id = self.create_tree_entry(parent, item['text'], 'item', item['content'])
        if selected_id and isinstance(data, dict):
            self.last_selected = selected_id
            self.tree.after(100, lambda: self.restore_selection())


    def restore_selection(self):
        if self.last_selected:
            try:
                self.tree.selection_set(self.last_selected)
                self.tree.see(self.last_selected)
                self.last_selected = None
            except:
                pass
