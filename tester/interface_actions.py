"""This module contains the InterfaceActions class, which is responsible for handling the GUI events for the Prompt Tester interface."""

# Standard Library
import os
import re


# Standard Library - GUI
from tkinter import filedialog
import tkinter as tk


class InterfaceActions:
    def __init__(self, interface, wildcard_manager, process_callback):
        self.interface = interface
        self.wildcard_manager = wildcard_manager
        self.process_callback = process_callback


    def on_text_change(self, event=None):
        if self.interface.live_var.get():
            self.process_callback()
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
