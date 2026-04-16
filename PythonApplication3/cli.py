"""
cli.py - Main CLI application for the Personal Finance Tracker.
"""

from datetime import datetime
from typing import Optional

from finance_tracker.analytics import Analytics
from finance_tracker.display import (
    clear_screen,
    display_accounts,
    display_budget_status,
    display_monthly_report,
    display_savings_goals,
    display_spending_trend,
    display_transactions,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    prompt_confirm,
    prompt_float,
    prompt_input,
    prompt_menu,
)
from finance_tracker.models import (
    Account,
    Budget,
    BudgetPeriod,
    Category,
    SavingsGoal,
    Transaction,
    TransactionType,
)
from finance_tracker.storage import FinanceStorage


class FinanceCLI:
    """Main CLI controller for the Personal Finance Tracker."""

    def __init__(self, data_dir: str = "data"):
        self.storage = FinanceStorage(data_dir)
        self.current_account: Optional[Account] = None

    def run(self):
        clear_screen()
        print_header(
            "💰 Personal Finance Tracker",
            "Your command-line companion for financial clarity"
        )
        self._main_menu()

    def _main_menu(self):
        while True:
            accounts = self.storage.load_accounts()
            account_label = (
                f"Account: {self.current_account.name}" if self.current_account else "No account selected"
            )
            choice = prompt_menu(
                [
                    f"Accounts  ({len(accounts)} total)",
                    f"Transactions  [{account_label}]",
                    "Budgets",
                    "Savings Goals",
                    "Reports & Analytics",
                    "Settings",
                ],
                title="🏠 Main Menu",
            )
            if choice == 0:
                if prompt_confirm("Exit Finance Tracker?"):
                    print_info("Goodbye! Stay financially fit 💪")
                    break
            elif choice == 1:
                self._accounts_menu()
            elif choice == 2:
                self._transactions_menu()
            elif choice == 3:
                self._budgets_menu()
            elif choice == 4:
                self._goals_menu()
            elif choice == 5:
                self._reports_menu()
            elif choice == 6:
                self._settings_menu()

    # ── Accounts ──────────────────────────────────────────────────────────────

    def _accounts_menu(self):
        while True:
            accounts = self.storage.load_accounts()
            display_accounts(accounts)
            choice = prompt_menu(
                ["Create Account", "Select Account", "Delete Account"],
                title="Accounts",
            )
            if choice == 0:
                break
            elif choice == 1:
                self._create_account()
            elif choice == 2:
                self._select_account(accounts)
            elif choice == 3:
                self._delete_account(accounts)

    def _create_account(self):
        print_info("Create a new account")
        name = prompt_input("Account name")
        if not name:
            print_error("Account name cannot be empty.")
            return
        account_types = ["checking", "savings", "investment", "cash", "credit"]
        type_choice = prompt_menu(account_types, "Account type")
        if type_choice == 0:
            return
        account_type = account_types[type_choice - 1]
        balance = prompt_float("Starting balance", 0.0)
        currency = prompt_input("Currency", "USD")
        account = Account(
            name=name,
            balance=balance,
            currency=currency,
            account_type=account_type,
        )
        self.storage.save_account(account)
        self.current_account = account
        print_success(f"Account '{name}' created and selected!")

    def _select_account(self, accounts):
        if not accounts:
            print_error("No accounts available. Create one first.")
            return
        choice = prompt_menu(
            [f"{a.name} — ${a.balance:,.2f}" for a in accounts],
            "Select an account",
        )
        if choice == 0:
            return
        self.current_account = accounts[choice - 1]
        print_success(f"Selected: {self.current_account.name}")

    def _delete_account(self, accounts):
        if not accounts:
            print_error("No accounts to delete.")
            return
        choice = prompt_menu([a.name for a in accounts], "Delete which account?")
        if choice == 0:
            return
        account = accounts[choice - 1]
        if prompt_confirm(f"Delete '{account.name}'? This cannot be undone."):
            self.storage.delete_account(account.id)
            if self.current_account and self.current_account.id == account.id:
                self.current_account = None
            print_success(f"Account '{account.name}' deleted.")

    # ── Transactions ──────────────────────────────────────────────────────────

    def _transactions_menu(self):
        if not self.current_account:
            print_warning("No account selected. Please select an account first.")
            accounts = self.storage.load_accounts()
            if accounts:
                self._select_account(accounts)
            else:
                return

        while True:
            choice = prompt_menu(
                ["Add Transaction", "View Recent Transactions", "Search Transactions", "View by Category"],
                title=f"Transactions — {self.current_account.name}",
            )
            if choice == 0:
                break
            elif choice == 1:
                self._add_transaction()
            elif choice == 2:
                self._view_recent_transactions()
            elif choice == 3:
                self._search_transactions()
            elif choice == 4:
                self._view_by_category()

    def _add_transaction(self):
        print_info("Add a new transaction")
        t_type_choice = prompt_menu(["Income", "Expense"], "Transaction type")
        if t_type_choice == 0:
            return
        t_type = TransactionType.INCOME if t_type_choice == 1 else TransactionType.EXPENSE

        if t_type == TransactionType.INCOME:
            income_cats = [
                Category.SALARY, Category.FREELANCE, Category.INVESTMENT,
                Category.GIFT, Category.OTHER_INCOME
            ]
            cat_choice = prompt_menu([c.value for c in income_cats], "Category")
            if cat_choice == 0:
                return
            category = income_cats[cat_choice - 1]
        else:
            expense_cats = [
                Category.HOUSING, Category.FOOD, Category.TRANSPORT,
                Category.HEALTHCARE, Category.ENTERTAINMENT, Category.EDUCATION,
                Category.CLOTHING, Category.UTILITIES, Category.SAVINGS,
                Category.DEBT, Category.OTHER_EXPENSE
            ]
            cat_choice = prompt_menu([c.value for c in expense_cats], "Category")
            if cat_choice == 0:
                return
            category = expense_cats[cat_choice - 1]

        amount = prompt_float("Amount")
        if amount <= 0:
            print_error("Amount must be positive.")
            return
        description = prompt_input("Description")
        notes = prompt_input("Notes (optional)", "")
        date_str = prompt_input("Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print_error("Invalid date format. Using today's date.")
            date = datetime.now()
        recurring = prompt_confirm("Is this a recurring transaction?")

        transaction = Transaction(
            amount=amount,
            category=category,
            transaction_type=t_type,
            description=description,
            date=date,
            notes=notes if notes else None,
            recurring=recurring,
        )
        self.current_account.add_transaction(transaction)
        self.storage.save_account(self.current_account)
        print_success(f"Transaction added! New balance: ${self.current_account.balance:,.2f}")

    def _view_recent_transactions(self):
        account = self.storage.get_account(self.current_account.id)
        if account:
            self.current_account = account
        display_transactions(
            self.current_account.transactions[-20:][::-1],
            title=f"Recent Transactions — {self.current_account.name}",
        )
        input("\nPress Enter to continue...")

    def _search_transactions(self):
        keyword = prompt_input("Search keyword (leave blank to skip)", "")
        min_amt_str = prompt_input("Min amount (leave blank to skip)", "")
        max_amt_str = prompt_input("Max amount (leave blank to skip)", "")
        min_amt = float(min_amt_str) if min_amt_str else None
        max_amt = float(max_amt_str) if max_amt_str else None
        accounts = self.storage.load_accounts()
        analytics = Analytics(accounts, [], [])
        results = analytics.find_transactions(
            keyword=keyword or None,
            min_amount=min_amt,
            max_amount=max_amt,
        )
        display_transactions(results, title=f"Search Results ({len(results)} found)")
        input("\nPress Enter to continue...")

    def _view_by_category(self):
        all_cats = list(Category)
        choice = prompt_menu([c.value for c in all_cats], "Select category")
        if choice == 0:
            return
        category = all_cats[choice - 1]
        transactions = self.current_account.get_transactions_by_category(category)
        display_transactions(transactions, title=f"Category: {category.value}")
        input("\nPress Enter to continue...")

    # ── Budgets ───────────────────────────────────────────────────────────────

    def _budgets_menu(self):
        while True:
            budgets = self.storage.load_budgets()
            choice = prompt_menu(
                [f"Add Budget ({len(budgets)} set)", "View Budget Status", "Delete Budget"],
                title="Budgets",
            )
            if choice == 0:
                break
            elif choice == 1:
                self._add_budget()
            elif choice == 2:
                self._view_budget_status()
            elif choice == 3:
                self._delete_budget(budgets)

    def _add_budget(self):
        print_info("Create a new budget")
        expense_cats = [
            Category.HOUSING, Category.FOOD, Category.TRANSPORT,
            Category.HEALTHCARE, Category.ENTERTAINMENT, Category.EDUCATION,
            Category.CLOTHING, Category.UTILITIES, Category.SAVINGS,
            Category.DEBT, Category.OTHER_EXPENSE
        ]
        choice = prompt_menu([c.value for c in expense_cats], "Category to budget")
        if choice == 0:
            return
        category = expense_cats[choice - 1]
        limit = prompt_float("Budget limit amount")
        period_options = [p.value for p in BudgetPeriod]
        period_choice = prompt_menu(period_options, "Budget period")
        if period_choice == 0:
            return
        period = BudgetPeriod(period_options[period_choice - 1])
        alert_pct = prompt_float("Alert at % (e.g. 80)", 80.0)
        budget = Budget(
            category=category,
            limit=limit,
            period=period,
            alert_threshold=alert_pct / 100,
        )
        self.storage.save_budget(budget)
        print_success(f"Budget created: ${limit:.2f}/{period.value} for {category.value}")

    def _view_budget_status(self):
        accounts = self.storage.load_accounts()
        budgets = self.storage.load_budgets()
        now = datetime.now()
        analytics = Analytics(accounts, budgets, [])
        statuses = analytics.budget_status(now.year, now.month)
        display_budget_status(statuses)
        input("\nPress Enter to continue...")

    def _delete_budget(self, budgets):
        if not budgets:
            print_error("No budgets to delete.")
            return
        choice = prompt_menu(
            [f"{b.category.value} — ${b.limit:.2f}/{b.period.value}" for b in budgets],
            "Delete which budget?",
        )
        if choice == 0:
            return
        budget = budgets[choice - 1]
        if prompt_confirm(f"Delete budget for {budget.category.value}?"):
            self.storage.delete_budget(budget.id)
            print_success("Budget deleted.")

    # ── Savings Goals ─────────────────────────────────────────────────────────

    def _goals_menu(self):
        while True:
            goals = self.storage.load_goals()
            display_savings_goals(goals)
            choice = prompt_menu(
                ["Add Goal", "Update Progress", "Delete Goal"],
                title="Savings Goals",
            )
            if choice == 0:
                break
            elif choice == 1:
                self._add_goal()
            elif choice == 2:
                self._update_goal_progress(goals)
            elif choice == 3:
                self._delete_goal(goals)

    def _add_goal(self):
        name = prompt_input("Goal name")
        target = prompt_float("Target amount")
        current = prompt_float("Current amount saved", 0.0)
        description = prompt_input("Description (optional)", "")
        deadline_str = prompt_input("Deadline (YYYY-MM-DD, optional)", "")
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                print_error("Invalid date. Skipping deadline.")
        goal = SavingsGoal(
            name=name,
            target_amount=target,
            current_amount=current,
            deadline=deadline,
            description=description if description else None,
        )
        self.storage.save_goal(goal)
        print_success(f"Goal '{name}' created! Target: ${target:,.2f}")

    def _update_goal_progress(self, goals):
        if not goals:
            print_error("No goals to update.")
            return
        choice = prompt_menu([g.name for g in goals], "Update which goal?")
        if choice == 0:
            return
        goal = goals[choice - 1]
        new_amount = prompt_float(f"New current amount (was ${goal.current_amount:,.2f})", goal.current_amount)
        goal.current_amount = new_amount
        self.storage.save_goal(goal)
        print_success(f"Progress updated! {goal.progress_percent:.1f}% complete.")

    def _delete_goal(self, goals):
        if not goals:
            print_error("No goals to delete.")
            return
        choice = prompt_menu([g.name for g in goals], "Delete which goal?")
        if choice == 0:
            return
        goal = goals[choice - 1]
        if prompt_confirm(f"Delete goal '{goal.name}'?"):
            self.storage.delete_goal(goal.id)
            print_success("Goal deleted.")

    # ── Reports ───────────────────────────────────────────────────────────────

    def _reports_menu(self):
        while True:
            choice = prompt_menu(
                ["Monthly Report", "6-Month Spending Trend", "Top Expenses", "Net Worth Trend"],
                title="Reports & Analytics",
            )
            if choice == 0:
                break
            elif choice == 1:
                self._monthly_report()
            elif choice == 2:
                self._spending_trend()
            elif choice == 3:
                self._top_expenses()
            elif choice == 4:
                self._net_worth()

    def _monthly_report(self):
        now = datetime.now()
        year_str = prompt_input("Year", str(now.year))
        month_str = prompt_input("Month (1-12)", str(now.month))
        try:
            year, month = int(year_str), int(month_str)
        except ValueError:
            print_error("Invalid year/month.")
            return
        accounts = self.storage.load_accounts()
        budgets = self.storage.load_budgets()
        goals = self.storage.load_goals()
        analytics = Analytics(accounts, budgets, goals)
        report = analytics.generate_report(year, month)
        display_monthly_report(report)
        input("\nPress Enter to continue...")

    def _spending_trend(self):
        accounts = self.storage.load_accounts()
        analytics = Analytics(accounts, [], [])
        trend = analytics.spending_trend(months=6)
        display_spending_trend(trend)
        input("\nPress Enter to continue...")

    def _top_expenses(self):
        accounts = self.storage.load_accounts()
        analytics = Analytics(accounts, [], [])
        now = datetime.now()
        top = analytics.top_expenses(now.year, now.month, n=10)
        display_transactions(top, title=f"Top Expenses — {datetime(now.year, now.month, 1).strftime('%B %Y')}")
        input("\nPress Enter to continue...")

    def _net_worth(self):
        accounts = self.storage.load_accounts()
        analytics = Analytics(accounts, [], [])
        net_worth = analytics.total_balance()
        print_info(f"Estimated Net Worth (Total Balance): ${net_worth:,.2f}")
        input("\nPress Enter to continue...")

    # ── Settings ──────────────────────────────────────────────────────────────

    def _settings_menu(self):
        while True:
            settings = self.storage.load_settings()
            choice = prompt_menu(
                [
                    f"Currency ({settings.get('currency', 'USD')})",
                    "Create Backup",
                    "View Data Location",
                ],
                title="Settings",
            )
            if choice == 0:
                break
            elif choice == 1:
                currency = prompt_input("Default currency code", settings.get("currency", "USD"))
                self.storage.update_setting("currency", currency.upper())
                print_success(f"Currency set to {currency.upper()}")
            elif choice == 2:
                backup_path = self.storage.backup()
                print_success(f"Backup created at: {backup_path}")
                input("\nPress Enter to continue...")
            elif choice == 3:
                print_info(f"Data directory: {self.storage.data_dir.resolve()}")
                input("\nPress Enter to continue...")
