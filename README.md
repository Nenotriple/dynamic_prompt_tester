# Dynamic Prompt Tester

A GUI for testing dynamic prompts with wildcards. Perfect for testing text generation prompts, templates, or any text that uses dynamic placeholders.

For more information regarding dynamic prompts: https://github.com/adieyal/sd-dynamic-prompts

## Features

### Prompt Tester
- **Live Processing**: See results in real-time as you type
- **Dynamic Prompt Syntax**: Use `Dynamic Prompt` syntax to insert dynamic content
- **Wildcard Support**: Use `__wildcard__` syntax to insert dynamic content
- **Fixed Seed Option**: Get consistent results for testing
- **Text Statistics**: Character, word, and estimated token counts
- **Collapsible Output**: Option to collapse output to a single line
- **Built-in Help**: Access help for syntax tips and usage

### Prompt Management
- **Save & Organize**: Store prompts in a hierarchical folder structure (JSON format)
- **Quick Search**: Find prompts by name or content
- **Import/Export**: Save and load your prompt library


## Usage
Currently the app is in early development.

Only sending prompts from the "Saved Prompts" tab to the "Prompt Tester" tab is supported. Saving/loading prompts from the "Prompt Tester" tab is not yet implemented.

### Basic Operation
1. Enter your text in the input pane
2. use `Dynamic Prompt` syntax to insert dynamic content
2. Use `__wildcard__` syntax to insert dynamic content
3. View the processed result in the output pane

### Wildcards
- Create .txt files in your wildcards folder
- Each file should contain one item per line
- Select the wildcards path using the "Browse..." button
  - The last selected path will be remembered
- Reference wildcards using `__filename__` syntax
- Example: `Hello __names__` will randomly select a name from names.txt

### Saving Prompts
1. Switch to the "Saved Prompts" tab
2. Create folders to organize your prompts
3. Add new prompts using the "New" menu
4. Edit and save prompts as needed
5. Your prompts/folders will be saved in JSON format


## Requirements
- Python 3.10+
- Pillow 11.0+
- TkToolTip 1.6+ = https://github.com/Nenotriple/TkToolTip


## To Run the GUI
1. Clone the repository
  - `git clone https://github.com/Nenotriple/TkToolTip.git`
2. Create a virtual environment/install dependencies/Start the GUI:
  - Run `Start.bat`
3. After the virtual environment is created you can change the `Start.bat` argument `set "FAST_START=FALSE"` to `set "FAST_START=TRUE"` to skip the dependency installation step in the future.
