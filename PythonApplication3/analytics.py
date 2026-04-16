"""
analytics.py - Financial analytics and reporting engine.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from finance_tracker.models import (
    Account,
    Budget,
    BudgetPeriod,
    Category,
    SavingsGoal,
    Transaction,
    TransactionType,
)


class Analytics:
    """
    Provides financial analysis, reports, and insights
    based on transaction and budget data.
    """

    def __init__(self, accounts: List[Account], budgets: List[Budget], goals: List[SavingsGoal]):
        self.accounts = accounts
        self.budgets = budgets
        self.goals = goals
        self._all_transactions = self._collect_all_transactions()

    def _collect_all_transactions(self) -> List[Transaction]:
        transactions = []
        for account in self.accounts:
            transactions.extend(account.transactions)
        return sorted(transactions, key=lambda t: t.date, reverse=True)

    def total_balance(self) -> float:
        return sum(acc.balance for acc in self.accounts)

    def total_income(self, year: int, month: Optional[int] = None) -> float:
        return self._sum_by_type(TransactionType.INCOME, year, month)

    def total_expenses(self, year: int, month: Optional[int] = None) -> float:
        return self._sum_by_type(TransactionType.EXPENSE, year, month)

    def net_savings(self, year: int, month: Optional[int] = None) -> float:
        return self.total_income(year, month) - self.total_expenses(year, month)

    def _sum_by_type(self, t_type: TransactionType, year: int, month: Optional[int]) -> float:
        total = 0.0
        for t in self._all_transactions:
            if t.transaction_type != t_type:
                continue
            if t.date.year != year:
                continue
            if month is not None and t.date.month != month:
                continue
            total += t.amount
        return total

    def spending_by_category(self, year: int, month: Optional[int] = None) -> Dict[Category, float]:
        breakdown = defaultdict(float)
        for t in self._all_transactions:
            if t.transaction_type != TransactionType.EXPENSE:
                continue
            if t.date.year != year:
                continue
            if month is not None and t.date.month != month:
                continue
            breakdown[t.category] += t.amount
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def income_by_category(self, year: int, month: Optional[int] = None) -> Dict[Category, float]:
        breakdown = defaultdict(float)
        for t in self._all_transactions:
            if t.transaction_type != TransactionType.INCOME:
                continue
            if t.date.year != year:
                continue
            if month is not None and t.date.month != month:
                continue
            breakdown[t.category] += t.amount
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def monthly_summary(self, year: int) -> List[Dict]:
        summaries = []
        for month in range(1, 13):
            income = self.total_income(year, month)
            expenses = self.total_expenses(year, month)
            summaries.append({
                "month": month,
                "month_name": datetime(year, month, 1).strftime("%B"),
                "income": income,
                "expenses": expenses,
                "net": income - expenses,
            })
        return summaries

    def budget_status(self, year: int, month: int) -> List[Dict]:
        spending = self.spending_by_category(year, month)
        statuses = []
        for budget in self.budgets:
            spent = spending.get(budget.category, 0.0)
            if budget.period == BudgetPeriod.WEEKLY:
                adjusted_limit = budget.limit * 4.33
            elif budget.period == BudgetPeriod.YEARLY:
                adjusted_limit = budget.limit / 12
            else:
                adjusted_limit = budget.limit
            usage_pct = (spent / adjusted_limit * 100) if adjusted_limit > 0 else 0
            statuses.append({
                "budget": budget,
                "spent": spent,
                "limit": adjusted_limit,
                "remaining": max(0.0, adjusted_limit - spent),
                "usage_percent": usage_pct,
                "over_budget": spent > adjusted_limit,
                "alert": usage_pct >= budget.alert_threshold * 100,
            })
        return sorted(statuses, key=lambda x: x["usage_percent"], reverse=True)

    def top_expenses(self, year: int, month: Optional[int] = None, n: int = 10) -> List[Transaction]:
        filtered = [
            t for t in self._all_transactions
            if t.transaction_type == TransactionType.EXPENSE
            and t.date.year == year
            and (month is None or t.date.month == month)
        ]
        return sorted(filtered, key=lambda t: t.amount, reverse=True)[:n]

    def recent_transactions(self, n: int = 20) -> List[Transaction]:
        return self._all_transactions[:n]

    def spending_trend(self, months: int = 6) -> List[Dict]:
        today = datetime.now()
        trend = []
        for i in range(months - 1, -1, -1):
            date = today - timedelta(days=30 * i)
            year, month = date.year, date.month
            trend.append({
                "label": date.strftime("%b %Y"),
                "income": self.total_income(year, month),
                "expenses": self.total_expenses(year, month),
            })
        return trend

    def savings_rate(self, year: int, month: int) -> float:
        income = self.total_income(year, month)
        if income == 0:
            return 0.0
        return (self.net_savings(year, month) / income) * 100

    def average_daily_spending(self, year: int, month: int) -> float:
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
        total = self.total_expenses(year, month)
        return total / days_in_month

    def recurring_transactions(self) -> List[Transaction]:
        return [t for t in self._all_transactions if t.recurring]

    def find_transactions(
        self,
        keyword: Optional[str] = None,
        category: Optional[Category] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        t_type: Optional[TransactionType] = None,
    ) -> List[Transaction]:
        results = self._all_transactions
        if keyword:
            kw = keyword.lower()
            results = [t for t in results if kw in t.description.lower() or (t.notes and kw in t.notes.lower())]
        if category:
            results = [t for t in results if t.category == category]
        if min_amount is not None:
            results = [t for t in results if t.amount >= min_amount]
        if max_amount is not None:
            results = [t for t in results if t.amount <= max_amount]
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if t_type:
            results = [t for t in results if t.transaction_type == t_type]
        return results

    def generate_report(self, year: int, month: int) -> Dict:
        return {
            "period": datetime(year, month, 1).strftime("%B %Y"),
            "total_income": self.total_income(year, month),
            "total_expenses": self.total_expenses(year, month),
            "net_savings": self.net_savings(year, month),
            "savings_rate": self.savings_rate(year, month),
            "avg_daily_spending": self.average_daily_spending(year, month),
            "top_expenses": self.top_expenses(year, month, n=5),
            "spending_by_category": self.spending_by_category(year, month),
            "budget_status": self.budget_status(year, month),
            "total_balance": self.total_balance(),
        }

    def net_worth_over_time(self) -> List[Tuple[str, float]]:
        """Approximate net worth trend based on running balance."""
        if not self._all_transactions:
            return []
        sorted_t = sorted(self._all_transactions, key=lambda t: t.date)
        balance = 0.0
        running = []
        for t in sorted_t:
            if t.transaction_type == TransactionType.INCOME:
                balance += t.amount
            elif t.transaction_type == TransactionType.EXPENSE:
                balance -= t.amount
            running.append((t.date.strftime("%Y-%m-%d"), round(balance, 2)))
        return running
