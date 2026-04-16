"""
models.py - Core data models for the Finance Tracker application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Category(Enum):
    # Income categories
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    GIFT = "gift"
    OTHER_INCOME = "other_income"

    # Expense categories
    HOUSING = "housing"
    FOOD = "food"
    TRANSPORT = "transport"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    CLOTHING = "clothing"
    UTILITIES = "utilities"
    SAVINGS = "savings"
    DEBT = "debt"
    OTHER_EXPENSE = "other_expense"


class BudgetPeriod(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Transaction:
    amount: float
    category: Category
    transaction_type: TransactionType
    description: str
    date: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: list = field(default_factory=list)
    recurring: bool = False
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category.value,
            "transaction_type": self.transaction_type.value,
            "description": self.description,
            "date": self.date.isoformat(),
            "tags": self.tags,
            "recurring": self.recurring,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            id=data["id"],
            amount=data["amount"],
            category=Category(data["category"]),
            transaction_type=TransactionType(data["transaction_type"]),
            description=data["description"],
            date=datetime.fromisoformat(data["date"]),
            tags=data.get("tags", []),
            recurring=data.get("recurring", False),
            notes=data.get("notes"),
        )

    def __str__(self) -> str:
        sign = "+" if self.transaction_type == TransactionType.INCOME else "-"
        return (
            f"[{self.date.strftime('%Y-%m-%d')}] "
            f"{sign}${self.amount:.2f} | "
            f"{self.category.value.upper()} | "
            f"{self.description}"
        )


@dataclass
class Budget:
    category: Category
    limit: float
    period: BudgetPeriod
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_threshold: float = 0.8  # Alert at 80% by default

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "limit": self.limit,
            "period": self.period.value,
            "alert_threshold": self.alert_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        return cls(
            id=data["id"],
            category=Category(data["category"]),
            limit=data["limit"],
            period=BudgetPeriod(data["period"]),
            alert_threshold=data.get("alert_threshold", 0.8),
        )


@dataclass
class Account:
    name: str
    balance: float
    currency: str = "USD"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_type: str = "checking"
    transactions: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance,
            "currency": self.currency,
            "account_type": self.account_type,
            "transactions": [t.to_dict() for t in self.transactions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        account = cls(
            id=data["id"],
            name=data["name"],
            balance=data["balance"],
            currency=data.get("currency", "USD"),
            account_type=data.get("account_type", "checking"),
        )
        account.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
        return account

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
        if transaction.transaction_type == TransactionType.INCOME:
            self.balance += transaction.amount
        elif transaction.transaction_type == TransactionType.EXPENSE:
            self.balance -= transaction.amount

    def get_transactions_by_month(self, year: int, month: int) -> list:
        return [
            t for t in self.transactions
            if t.date.year == year and t.date.month == month
        ]

    def get_transactions_by_category(self, category: Category) -> list:
        return [t for t in self.transactions if t.category == category]

    def __str__(self) -> str:
        return f"{self.name} ({self.account_type}) | Balance: ${self.balance:.2f} {self.currency}"


@dataclass
class SavingsGoal:
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None

    @property
    def progress_percent(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return (self.current_amount / self.target_amount) * 100

    @property
    def remaining(self) -> float:
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def is_complete(self) -> bool:
        return self.current_amount >= self.target_amount

    def days_remaining(self) -> Optional[int]:
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.now()
        return max(0, delta.days)

    def monthly_savings_needed(self) -> Optional[float]:
        days = self.days_remaining()
        if days is None or days == 0:
            return None
        months = days / 30.0
        return self.remaining / months if months > 0 else None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SavingsGoal":
        return cls(
            id=data["id"],
            name=data["name"],
            target_amount=data["target_amount"],
            current_amount=data["current_amount"],
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            description=data.get("description"),
        )

    def __str__(self) -> str:
        bar_length = 20
        filled = int((self.progress_percent / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        return (
            f"{self.name}: [{bar}] {self.progress_percent:.1f}%\n"
            f"  ${self.current_amount:.2f} / ${self.target_amount:.2f} "
            f"(${self.remaining:.2f} remaining)"
        )
