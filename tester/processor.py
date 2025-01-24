"""TextProcessor class for processing text with wildcards and variants."""

import random
import re


#endregion
##################################################
#region Samplers
class BaseSampler:
    def sample(self, options):
        raise NotImplementedError()


class RandomSampler(BaseSampler):
    def sample(self, options):
        return random.choice(options)


class CyclicalSampler(BaseSampler):
    def __init__(self):
        self.indices = {}


    def sample(self, options):
        key = tuple(options)
        if key not in self.indices:
            self.indices[key] = 0
        else:
            self.indices[key] = (self.indices[key] + 1) % len(options)
        return options[self.indices[key]]


class CombinatorialSampler(BaseSampler):
    def __init__(self):
        self.combinations = {}
        self.indices = {}


    def sample(self, options):
        key = tuple(options)
        if key not in self.combinations:
            self.combinations[key] = list(options)
            self.indices[key] = 0
        if self.indices[key] >= len(self.combinations[key]):
            return None
        result = self.combinations[key][self.indices[key]]
        self.indices[key] += 1
        return result


#endregion
##################################################
#region TextProcessor
class TextProcessor:
    def __init__(self, wildcard_manager):
        self.initialize_variant_regex()
        self.initialize_wildcard_regex()
        self.random_sampler = RandomSampler()
        self.cyclical_sampler = CyclicalSampler()
        self.combinatorial_sampler = CombinatorialSampler()
        self.default_sampler = self.random_sampler
        self.wildcard_manager = wildcard_manager


    def initialize_variant_regex(self):
        self.variant_pattern = re.compile(r'''
            {                    # Opening brace
            ([~@&])?             # Optional prefix (~, @, or &)
            (?:                  # Start of count/separator group
                (\d+(?:-\d+)?)   # Count (e.g., 2 or 1-3)
                \$\$             # Double-dollar separator
                (?:              # Start of optional separator
                    ([^${}|]*)   # Separator content
                    \$\$         # Double-dollar separator
                )?               # End of optional separator
            )?                   # End of count/separator group
            ([^{}]*              # Content: non-brace chars
            (?:{[^{}]*}[^{}]*)*  # Nested brace patterns
            )                    # End of content group
            }                    # Closing brace
        ''', re.VERBOSE)


    def initialize_wildcard_regex(self):
        self.wildcard_pattern = re.compile(r'''
            __              # Opening double-underscore
            ([~@&])?        # Optional prefix (~, @, or &)
            ([^_\s]+        # First part of wildcard name
            (?:_[^_\s]+)*   # Allow additional parts with underscores
            )               # End of wildcard name group
            __              # Closing double-underscore
        ''', re.VERBOSE)


    def get_sampler(self, prefix):
        if prefix == '~':
            return self.random_sampler
        elif prefix == '@':
            return self.cyclical_sampler
        elif prefix == '$':
            return self.combinatorial_sampler
        return self.default_sampler


    def parse_selection_count(self, count_str):
        if not count_str:
            return 1, 1
        if '-' in count_str:
            min_count, max_count = map(int, count_str.split('-'))
            return min_count or 1, max_count
        return int(count_str), int(count_str)


    def process_variant(self, match):
        prefix = match.group(1)
        count_str = match.group(2)
        separator = match.group(3) or ', '
        content = match.group(4)
        if '{' in content:
            content = self.variant_pattern.sub(self.process_variant, content)
        options = []
        current = []
        brace_count = 0
        for char in content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '|' and brace_count == 0:
                options.append(''.join(current).strip())
                current = []
                continue
            current.append(char)
        options.append(''.join(current).strip())
        sampler = self.get_sampler(prefix)
        if count_str:
            min_count, max_count = self.parse_selection_count(count_str)
            count = random.randint(min_count, max_count)
            count = min(count, len(options))
            selected = random.sample(options, count)
            return separator.join(selected)
        result = sampler.sample(options)
        return result if result is not None else options[0]


    def process_wildcard(self, match):
        prefix = match.group(1)
        wildcard_name = match.group(2)
        options = self.wildcard_manager.get_wildcard_options(wildcard_name)
        if not options:
            return f"__{wildcard_name}__"
        sampler = self.get_sampler(prefix)
        result = sampler.sample(options)
        return result if result is not None else options[0]


    def process(self, text):
        text = self.wildcard_pattern.sub(self.process_wildcard, text)
        return self.variant_pattern.sub(self.process_variant, text)


    def set_default_sampler(self, sampler_type):
        if sampler_type == 'random':
            self.default_sampler = self.random_sampler
        elif sampler_type == 'cyclical':
            self.default_sampler = self.cyclical_sampler
        elif sampler_type == 'combinatorial':
            self.default_sampler = self.combinatorial_sampler
