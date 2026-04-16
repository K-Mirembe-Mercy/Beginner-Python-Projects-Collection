"""
tests/test_models.py - Unit tests for Finance Tracker models.
"""

import unittest
from datetime import datetime, timedelta

from finance_tracker.models import (
    Account,
    Budget,
    BudgetPeriod,
    Category,
    SavingsGoal,
    Transaction,
    TransactionType,
)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.income_tx = Transaction(
            amount=3000.0,
            category=Category.SALARY,
            transaction_type=TransactionType.INCOME,
            description="Monthly salary",
        )
        self.expense_tx = Transaction(
            amount=150.0,
            category=Category.FOOD,
            transaction_type=TransactionType.EXPENSE,
            description="Groceries",
            tags=["weekly", "essentials"],
        )

    def test_transaction_creation(self):
        self.assertEqual(self.income_tx.amount, 3000.0)
        self.assertEqual(self.income_tx.category, Category.SALARY)
        self.assertEqual(self.income_tx.transaction_type, TransactionType.INCOME)
        self.assertIsNotNone(self.income_tx.id)

    def test_transaction_serialization(self):
        d = self.income_tx.to_dict()
        self.assertEqual(d["amount"], 3000.0)
        self.assertEqual(d["category"], "salary")
        self.assertEqual(d["transaction_type"], "income")
        restored = Transaction.from_dict(d)
        self.assertEqual(restored.id, self.income_tx.id)
        self.assertEqual(restored.amount, self.income_tx.amount)

    def test_tags_preserved(self):
        d = self.expense_tx.to_dict()
        restored = Transaction.from_dict(d)
        self.assertEqual(restored.tags, ["weekly", "essentials"])

    def test_str_representation_income(self):
        s = str(self.income_tx)
        self.assertIn("+$3000.00", s)
        self.assertIn("SALARY", s)

    def test_str_representation_expense(self):
        s = str(self.expense_tx)
        self.assertIn("-$150.00", s)
        self.assertIn("FOOD", s)


class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account(name="Checking", balance=1000.0)
        self.income_tx = Transaction(
            amount=500.0,
            category=Category.SALARY,
            transaction_type=TransactionType.INCOME,
            description="Bonus",
        )
        self.expense_tx = Transaction(
            amount=200.0,
            category=Category.FOOD,
            transaction_type=TransactionType.EXPENSE,
            description="Dinner",
        )

    def test_add_income_updates_balance(self):
        self.account.add_transaction(self.income_tx)
        self.assertAlmostEqual(self.account.balance, 1500.0)

    def test_add_expense_updates_balance(self):
        self.account.add_transaction(self.expense_tx)
        self.assertAlmostEqual(self.account.balance, 800.0)

    def test_multiple_transactions(self):
        self.account.add_transaction(self.income_tx)
        self.account.add_transaction(self.expense_tx)
        self.assertAlmostEqual(self.account.balance, 1300.0)
        self.assertEqual(len(self.account.transactions), 2)

    def test_serialization_roundtrip(self):
        self.account.add_transaction(self.income_tx)
        d = self.account.to_dict()
        restored = Account.from_dict(d)
        self.assertEqual(restored.id, self.account.id)
        self.assertEqual(restored.name, "Checking")
        self.assertAlmostEqual(restored.balance, 1500.0)
        self.assertEqual(len(restored.transactions), 1)

    def test_get_transactions_by_category(self):
        self.account.add_transaction(self.income_tx)
        self.account.add_transaction(self.expense_tx)
        salary_txs = self.account.get_transactions_by_category(Category.SALARY)
        self.assertEqual(len(salary_txs), 1)
        self.assertEqual(salary_txs[0].description, "Bonus")

    def test_get_transactions_by_month(self):
        now = datetime.now()
        last_month = now - timedelta(days=35)
        old_tx = Transaction(
            amount=100.0,
            category=Category.FOOD,
            transaction_type=TransactionType.EXPENSE,
            description="Old expense",
            date=last_month,
        )
        self.account.add_transaction(self.expense_tx)
        self.account.add_transaction(old_tx)
        current_txs = self.account.get_transactions_by_month(now.year, now.month)
        self.assertEqual(len(current_txs), 1)

    def test_account_str(self):
        s = str(self.account)
        self.assertIn("Checking", s)
        self.assertIn("1000.00", s)


class TestBudget(unittest.TestCase):

    def test_budget_creation(self):
        budget = Budget(
            category=Category.FOOD,
            limit=500.0,
            period=BudgetPeriod.MONTHLY,
        )
        self.assertEqual(budget.category, Category.FOOD)
        self.assertEqual(budget.limit, 500.0)
        self.assertEqual(budget.alert_threshold, 0.8)

    def test_budget_serialization(self):
        budget = Budget(
            category=Category.TRANSPORT,
            limit=200.0,
            period=BudgetPeriod.WEEKLY,
            alert_threshold=0.9,
        )
        d = budget.to_dict()
        restored = Budget.from_dict(d)
        self.assertEqual(restored.id, budget.id)
        self.assertEqual(restored.category, Category.TRANSPORT)
        self.assertEqual(restored.alert_threshold, 0.9)


class TestSavingsGoal(unittest.TestCase):

    def test_goal_progress(self):
        goal = SavingsGoal(name="Emergency Fund", target_amount=10000.0, current_amount=2500.0)
        self.assertAlmostEqual(goal.progress_percent, 25.0)
        self.assertAlmostEqual(goal.remaining, 7500.0)
        self.assertFalse(goal.is_complete)

    def test_goal_complete(self):
        goal = SavingsGoal(name="Vacation", target_amount=2000.0, current_amount=2000.0)
        self.assertTrue(goal.is_complete)
        self.assertAlmostEqual(goal.progress_percent, 100.0)

    def test_goal_over_target(self):
        goal = SavingsGoal(name="Car", target_amount=5000.0, current_amount=5500.0)
        self.assertTrue(goal.is_complete)
        self.assertAlmostEqual(goal.remaining, 0.0)

    def test_days_remaining(self):
        future = datetime.now() + timedelta(days=90)
        goal = SavingsGoal(name="Test", target_amount=1000.0, deadline=future)
        days = goal.days_remaining()
        self.assertIsNotNone(days)
        self.assertGreater(days, 85)
        self.assertLessEqual(days, 91)

    def test_monthly_savings_needed(self):
        future = datetime.now() + timedelta(days=120)  # ~4 months
        goal = SavingsGoal(name="Test", target_amount=4000.0, current_amount=0.0, deadline=future)
        monthly = goal.monthly_savings_needed()
        self.assertIsNotNone(monthly)
        self.assertAlmostEqual(monthly, 1000.0, delta=50.0)

    def test_serialization_roundtrip(self):
        future = datetime(2026, 12, 31)
        goal = SavingsGoal(
            name="House Down Payment",
            target_amount=50000.0,
            current_amount=12000.0,
            deadline=future,
            description="Save for house",
        )
        d = goal.to_dict()
        restored = SavingsGoal.from_dict(d)
        self.assertEqual(restored.id, goal.id)
        self.assertEqual(restored.name, "House Down Payment")
        self.assertAlmostEqual(restored.target_amount, 50000.0)
        self.assertEqual(restored.deadline.year, 2026)

    def test_zero_target_progress(self):
        goal = SavingsGoal(name="Empty", target_amount=0.0, current_amount=100.0)
        self.assertAlmostEqual(goal.progress_percent, 0.0)

    def test_str_output(self):
        goal = SavingsGoal(name="Laptop", target_amount=2000.0, current_amount=500.0)
        s = str(goal)
        self.assertIn("Laptop", s)
        self.assertIn("25.0%", s)


class TestAnalyticsIntegration(unittest.TestCase):
    """Integration tests that bring multiple models together."""

    def setUp(self):
        from finance_tracker.analytics import Analytics

        self.account = Account(name="Main", balance=0.0)
        now = datetime.now()
        transactions = [
            Transaction(3000.0, Category.SALARY, TransactionType.INCOME, "Salary", now),
            Transaction(200.0, Category.FREELANCE, TransactionType.INCOME, "Side gig", now),
            Transaction(1200.0, Category.HOUSING, TransactionType.EXPENSE, "Rent", now),
            Transaction(300.0, Category.FOOD, TransactionType.EXPENSE, "Groceries", now),
            Transaction(100.0, Category.TRANSPORT, TransactionType.EXPENSE, "Gas", now),
            Transaction(50.0, Category.ENTERTAINMENT, TransactionType.EXPENSE, "Movies", now),
        ]
        for t in transactions:
            self.account.add_transaction(t)

        budget = Budget(Category.FOOD, 400.0, BudgetPeriod.MONTHLY)
        self.analytics = Analytics([self.account], [budget], [])

    def test_total_income(self):
        now = datetime.now()
        income = self.analytics.total_income(now.year, now.month)
        self.assertAlmostEqual(income, 3200.0)

    def test_total_expenses(self):
        now = datetime.now()
        expenses = self.analytics.total_expenses(now.year, now.month)
        self.assertAlmostEqual(expenses, 1650.0)

    def test_net_savings(self):
        now = datetime.now()
        net = self.analytics.net_savings(now.year, now.month)
        self.assertAlmostEqual(net, 1550.0)

    def test_savings_rate(self):
        now = datetime.now()
        rate = self.analytics.savings_rate(now.year, now.month)
        self.assertAlmostEqual(rate, (1550.0 / 3200.0) * 100, delta=0.1)

    def test_spending_by_category(self):
        now = datetime.now()
        breakdown = self.analytics.spending_by_category(now.year, now.month)
        self.assertAlmostEqual(breakdown[Category.HOUSING], 1200.0)
        self.assertAlmostEqual(breakdown[Category.FOOD], 300.0)

    def test_top_expenses(self):
        now = datetime.now()
        top = self.analytics.top_expenses(now.year, now.month, n=3)
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0].category, Category.HOUSING)

    def test_budget_status_ok(self):
        now = datetime.now()
        statuses = self.analytics.budget_status(now.year, now.month)
        food_status = next(s for s in statuses if s["budget"].category == Category.FOOD)
        self.assertFalse(food_status["over_budget"])
        self.assertAlmostEqual(food_status["spent"], 300.0)

    def test_total_balance(self):
        balance = self.analytics.total_balance()
        self.assertAlmostEqual(balance, self.account.balance)


if __name__ == "__main__":
    unittest.main(verbosity=2)
