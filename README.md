# Habit Tracker (CLI) — Modular, Tested, and PEP 8–friendly

A command-line habit tracker designed for clean Python project structure.

Features include:
- Modular design (`app/models`, `app/db`, `app/analysis`)
- Periodicity-aware streak logic (daily / weekly / monthly)
- Analytics module
- 5 predefined demo habits (3 daily, 2 weekly)
- Completion history with timestamps
- SQLite persistence (`habits.sqlite3` file)
- Unit tests for habit tracking and analytics
- Setup with `.gitignore` and `requirements.txt`

---

## Requirements

- Python 3.11+
- (Windows) PowerShell or Command Prompt
- Git and VS Code


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


