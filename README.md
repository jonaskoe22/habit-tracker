# Habit Tracker (CLI) — Modular, Tested, and PEP 8–friendly

A command-line habit tracker designed for clean Python project structure.

Features include:
- Modular design (`app/models`, `app/db`, `app/analysis`)
- Periodicity-aware streak logic (daily / weekly / monthly)
- Analytics module implemented in functional style
- 5 predefined demo habits (3 daily, 2 weekly)
- Completion history with timestamps
- SQLite persistence (`habits.sqlite3` file)
- Unit tests for habit tracking and analytics
- Easy setup with `.gitignore` and `requirements.txt`

---

## Requirements

- Python 3.11+
- (Windows) PowerShell or Command Prompt
- (Recommended) Git and VS Code

Tip (Windows): If PowerShell blocks venv activation, use the batch activator  
`.venv\Scripts\activate.bat` instead of `Activate.ps1`.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/jonaskoe22/habit-tracker.git
cd habit-tracker

# Create a virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (recommended)
pytest -q

# Run the application
python -m app.cli
