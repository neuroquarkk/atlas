# Atlas - Project-Scoped Codebase Indexer & Search Tool

Atlas is a fast, local CLI tool designed to index your Python projects. It uses Python's Abstract Syntax Tree (AST) to parse source code making it significantly faster and more accurate than regex-based searching. It allows you to instantly locate classes, functions and methods across your project

## Features

- **Fast Indexing:** uses an optimized `O(n)` ast visitor to parse files in a single pass
- **Symbol Search:** instantly find definitions of classes, functions and methods
- **Beautiful UI:** powered by `Rich` for colorful, structured and easy to read output
- **Project Aware:** automatically manages a local `.atlas` metadata directory and updates your `.gitignore` to keep your repo clean
- **Grouped Results:** search results are displayed in a clean file tree hierarchy

## Installation

### Setup from source

1. Clone the repository:

```bash
git clone https://github.com/neuroquarkk/atlas.git
cd atlas
```

2. Install dependencies:

```bash
uv sync
```

3. Compile:

```bash
uv add --dev pyinstaller
pyinstaller --onefile --name atlas --paths src --optimize 1 --clean main.py
```

## Usage

### 1. Initialize a project

Run this in the root of the project you want to index. This creates the `.atlas` directory and ensures it is added to `.gitignore`

```bash
atlas init
```

### 2. Index the codebase

Parses all `.py` files and builds the symbol database

```bash
atlas index
```

### 3. Search for symbols

Find where a specific class or function is defined

```bash
atlas search project
```

### 4. Check status

View the current project root and when the index was last updated

```bash
atlas status
```
