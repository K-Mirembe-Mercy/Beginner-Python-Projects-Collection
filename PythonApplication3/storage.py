"""
storage.py - Handles persistence for the Finance Tracker using JSON files.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from finance_tracker.models import Account, Budget, SavingsGoal, Transaction


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


class FinanceStorage:
    """
    Manages all data persistence for the Finance Tracker.
    Uses JSON files for portability and human-readability.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.accounts_file = self.data_dir / "accounts.json"
        self.budgets_file = self.data_dir / "budgets.json"
        self.goals_file = self.data_dir / "goals.json"
        self.settings_file = self.data_dir / "settings.json"
        self._ensure_data_dir()
        self._initialize_files()

    def _ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)

    def _initialize_files(self) -> None:
        defaults = {
            self.accounts_file: [],
            self.budgets_file: [],
            self.goals_file: [],
            self.settings_file: {
                "currency": "USD",
                "theme": "default",
                "date_format": "%Y-%m-%d",
                "created_at": datetime.now().isoformat(),
            },
        }
        for filepath, default in defaults.items():
            if not filepath.exists():
                self._write_json(filepath, default)

    def _read_json(self, filepath: Path) -> any:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StorageError(f"Corrupted data file {filepath}: {e}")
        except FileNotFoundError:
            raise StorageError(f"Data file not found: {filepath}")

    def _write_json(self, filepath: Path, data: any) -> None:
        try:
            tmp_file = filepath.with_suffix(".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp_file.replace(filepath)
        except IOError as e:
            raise StorageError(f"Failed to write data to {filepath}: {e}")

    def backup(self) -> str:
        """Create a timestamped backup of all data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.data_dir / "backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        files_backed_up = []
        for filepath in [self.accounts_file, self.budgets_file, self.goals_file, self.settings_file]:
            if filepath.exists():
                dest = backup_dir / filepath.name
                shutil.copy2(filepath, dest)
                files_backed_up.append(filepath.name)
        return str(backup_dir)

    # ── Accounts ──────────────────────────────────────────────────────────────

    def load_accounts(self) -> List[Account]:
        data = self._read_json(self.accounts_file)
        return [Account.from_dict(a) for a in data]

    def save_accounts(self, accounts: List[Account]) -> None:
        self._write_json(self.accounts_file, [a.to_dict() for a in accounts])

    def get_account(self, account_id: str) -> Optional[Account]:
        accounts = self.load_accounts()
        return next((a for a in accounts if a.id == account_id), None)

    def save_account(self, account: Account) -> None:
        accounts = self.load_accounts()
        existing_idx = next((i for i, a in enumerate(accounts) if a.id == account.id), None)
        if existing_idx is not None:
            accounts[existing_idx] = account
        else:
            accounts.append(account)
        self.save_accounts(accounts)

    def delete_account(self, account_id: str) -> bool:
        accounts = self.load_accounts()
        original_len = len(accounts)
        accounts = [a for a in accounts if a.id != account_id]
        if len(accounts) < original_len:
            self.save_accounts(accounts)
            return True
        return False

    # ── Budgets ───────────────────────────────────────────────────────────────

    def load_budgets(self) -> List[Budget]:
        data = self._read_json(self.budgets_file)
        return [Budget.from_dict(b) for b in data]

    def save_budgets(self, budgets: List[Budget]) -> None:
        self._write_json(self.budgets_file, [b.to_dict() for b in budgets])

    def save_budget(self, budget: Budget) -> None:
        budgets = self.load_budgets()
        existing_idx = next((i for i, b in enumerate(budgets) if b.id == budget.id), None)
        if existing_idx is not None:
            budgets[existing_idx] = budget
        else:
            budgets.append(budget)
        self.save_budgets(budgets)

    def delete_budget(self, budget_id: str) -> bool:
        budgets = self.load_budgets()
        original_len = len(budgets)
        budgets = [b for b in budgets if b.id != budget_id]
        if len(budgets) < original_len:
            self.save_budgets(budgets)
            return True
        return False

    # ── Savings Goals ─────────────────────────────────────────────────────────

    def load_goals(self) -> List[SavingsGoal]:
        data = self._read_json(self.goals_file)
        return [SavingsGoal.from_dict(g) for g in data]

    def save_goals(self, goals: List[SavingsGoal]) -> None:
        self._write_json(self.goals_file, [g.to_dict() for g in goals])

    def save_goal(self, goal: SavingsGoal) -> None:
        goals = self.load_goals()
        existing_idx = next((i for i, g in enumerate(goals) if g.id == goal.id), None)
        if existing_idx is not None:
            goals[existing_idx] = goal
        else:
            goals.append(goal)
        self.save_goals(goals)

    def delete_goal(self, goal_id: str) -> bool:
        goals = self.load_goals()
        original_len = len(goals)
        goals = [g for g in goals if g.id != goal_id]
        if len(goals) < original_len:
            self.save_goals(goals)
            return True
        return False

    # ── Settings ──────────────────────────────────────────────────────────────

    def load_settings(self) -> Dict:
        return self._read_json(self.settings_file)

    def save_settings(self, settings: Dict) -> None:
        self._write_json(self.settings_file, settings)

    def update_setting(self, key: str, value: any) -> None:
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
