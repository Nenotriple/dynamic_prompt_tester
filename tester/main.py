"""Main entry point for the Prompt Tester tab and interface."""

# Standard Library
import random

# Local Imports
from tester.wildcard_manager import WildcardManager
from tester.processor import TextProcessor
from tester.interface import Interface


# Main Application
class PromptTester:
    def __init__(self, root, tab):
        self.wildcard_manager = WildcardManager()
        self.processor = TextProcessor(self.wildcard_manager)
        self.ui = Interface(root, self, tab)

    def set_random_seed(self):
        if self.ui.is_fixed_seed():
            random.seed(42)
        else:
            random.seed()

    def process_text(self):
        text = self.ui.actions.get_input_text()
        self.set_random_seed()
        processed_text = self.processor.process(text)
        self.ui.actions.display_text_output(processed_text)
