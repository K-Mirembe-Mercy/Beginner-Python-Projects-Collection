# 💰 Personal Finance Tracker

A feature-rich command-line personal finance tracker built in Python.

## Features

- **Multiple Accounts** — checking, savings, investment, cash, credit
- **Transaction Tracking** — income & expenses with categories, tags, and notes
- **Budget Management** — set spending limits with configurable alerts
- **Savings Goals** — track progress with deadlines and monthly targets
- **Analytics & Reports** — monthly summaries, spending trends, category breakdowns
- **Data Persistence** — all data saved locally as JSON with automatic backups
- **Rich Terminal UI** — colorful tables and progress bars (requires `rich`)

## Installation

```bash
git clone https://github.com/yourusername/finance-tracker.git
cd finance-tracker
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

With a custom data directory:
```bash
python main.py --data-dir ~/my_finances
```

## Run Tests

```bash
python -m pytest tests/ -v
# or
python -m unittest discover tests
```

## Project Structure

```
finance_tracker/
├── finance_tracker/
│   ├── __init__.py
│   ├── models.py       # Core data models (Transaction, Account, Budget, SavingsGoal)
│   ├── storage.py      # JSON persistence layer
│   ├── analytics.py    # Financial analytics engine
│   ├── display.py      # Terminal UI rendering
│   └── cli.py          # CLI menus and controllers
├── tests/
│   └── test_models.py  # Unit & integration tests
├── main.py             # Entry point
├── requirements.txt
└── setup.py
```

## Categories

**Income:** Salary, Freelance, Investment, Gift, Other  
**Expenses:** Housing, Food, Transport, Healthcare, Entertainment, Education, Clothing, Utilities, Savings, Debt, Other

## Data

All data is stored in the `data/` directory as JSON files:
- `accounts.json` — accounts and their transactions
- `budgets.json` — budget limits
- `goals.json` — savings goals
- `settings.json` — app settings
- `backups/` — timestamped backups
