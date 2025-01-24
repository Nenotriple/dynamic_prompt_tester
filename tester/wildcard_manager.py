"""Wildcard Manager handles the loading and caching of wildcard files."""


import os


class WildcardManager:
    def __init__(self):
        self.wildcards_path = None
        self.wildcard_cache = {}
        self.available_wildcards = set()
        self.initialize_last_path_file()
        self.load_last_path()


    def initialize_last_path_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        target_dir = os.path.join(parent_dir, 'config')
        self.last_path_file = os.path.join(target_dir, "last_wildcard_path.txt")


    def set_wildcards_path(self, path):
        self.wildcards_path = os.path.normpath(path)
        if path:
            self.save_last_path(path)
        self.load_wildcard_files()


    def save_last_path(self, path):
        try:
            with open(self.last_path_file, "w", encoding="utf-8") as file:
                file.write(path)
        except Exception as e:
            print(f"ERROR - save_last_path(): {e}")


    def load_last_path(self):
        if not os.path.exists(self.last_path_file):
            return
        try:
            with open(self.last_path_file, "r", encoding="utf-8") as file:
                path = file.read().strip()
                if path and os.path.isdir(path):
                    self.set_wildcards_path(path)
        except Exception as e:
            print(f"ERROR - load_last_path(): {e}")


    def load_wildcard_files(self):
        if not self.wildcards_path:
            return
        self.wildcard_cache.clear()
        self.available_wildcards.clear()
        for file_name in os.listdir(self.wildcards_path):
            if not file_name.endswith(".txt"):
                continue
            base_name = os.path.splitext(file_name)[0]
            self.available_wildcards.add(base_name)
            self.load_wildcard(base_name)


    def load_wildcard(self, wildcard_name):
        if not self.wildcards_path:
            return None
        # Return cached content if available
        if wildcard_name in self.wildcard_cache:
            return self.wildcard_cache[wildcard_name]
        # Load from file
        wildcard_file = os.path.join(self.wildcards_path, f"{wildcard_name}.txt")
        if not os.path.exists(wildcard_file):
            return None
        try:
            with open(wildcard_file, 'r', encoding='utf-8') as f:
                options = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                if options:
                    self.wildcard_cache[wildcard_name] = options
                    return options
        except Exception as e:
            print(f"ERROR - load_wildcard(): {e}")
        return None


    def get_wildcard_options(self, wildcard_name):
        return self.load_wildcard(wildcard_name)


    def get_available_wildcards(self):
        return sorted(list(self.available_wildcards))


    def reload_wildcards(self):
        self.wildcard_cache.clear()
        self.load_wildcard_files()
