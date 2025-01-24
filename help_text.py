HELP_TEXT = """
📝 Basic Usage
--------------
• Type your prompt in the 'Input' box
• Enable 'Live Processing' for real-time updates or use 'Process Text' button
• Lines/Comments starting with # are ignored
• Use 'Collapse Output' to convert newlines to spaces
• 'Fixed Seed' ensures consistent random choices


🎲 Variants - Basic Usage
-------------------------
Format: {option1|option2|option3}
Examples:
• Simple:    {red|green|blue}               →   picks one
• Weighted:  {2::red|1::blue}               →   red twice as likely
• Nested:    a {2$${big|small}|{dog|cat}}   →   "a dog, small", "a small, cat", etc.


🎲 Variants - Advanced Features
-------------------------------
Multiple Selection:
• Basic:     {2$$red|green|blue}        →   "red, blue"
• Range:     {1-3$$red|green|blue}      →   picks 1 to 3 items (", " separator)
• Custom:    {2$$, and $$red|green}     →   "red, and green" (Custom separator)


📁 Wildcards
------------
Format: __wildcard__   (pulls from wildcard.txt)

Features:
• Wildcards are loaded from the selected directory
• Double-click wildcards in the sidebar to insert
• # comments in wildcard files are ignored
• Wildcards can contain variants
• Variants can contain wildcards

Examples:
• Basic:     __season__
• Multiple:  __2$$weather__


🎯 Samplers - Control Random Behavior
-------------------------------------
Prefix any variant or wildcard with:
• Random (~):   {~red|green|blue}    Default behavior
• Cycle (@):    {@red|green|blue}    Cycles in order
• All (&):      {&red|green|blue}    Uses each once

Examples:
• Mixed:        {The {@big|small} {~dog|cat}}
• Wildcard:     __@weather__   __~season__


💡 Tips & Tricks
----------------
• Only .txt wildcard files are supported
• Use nesting for complex combinations
• Combine samplers for precise control
• Enable Fixed Seed for testing
• Stats bar shows character/word/token counts
• NOTE: This tool is a simplified version of the official Dynamic Prompts tool, some features like Weighting Options, Omitting Bounds, etc. are not available here.

• The official Syntax documentation is available at: https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/SYNTAX.md
"""
