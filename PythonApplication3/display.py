"""
display.py - Terminal display utilities using rich-style formatting.
Falls back to plain text if rich is not installed.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from finance_tracker.models import Account, Budget, Category, SavingsGoal, Transaction, TransactionType

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    from rich.columns import Columns
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str, subtitle: str = ""):
    if RICH_AVAILABLE:
        text = Text(title, style="bold cyan")
        if subtitle:
            text.append(f"\n{subtitle}", style="dim")
        console.print(Panel(text, border_style="cyan", padding=(1, 4)))
    else:
        print("\n" + "=" * 60)
        print(f"  {title}")
        if subtitle:
            print(f"  {subtitle}")
        print("=" * 60)


def print_success(message: str):
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/bold green] {message}")
    else:
        print(f"[OK] {message}")


def print_error(message: str):
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/bold red] {message}")
    else:
        print(f"[ERROR] {message}")


def print_warning(message: str):
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠[/bold yellow]  {message}")
    else:
        print(f"[WARN] {message}")


def print_info(message: str):
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ[/bold blue]  {message}")
    else:
        print(f"[INFO] {message}")


def display_accounts(accounts: List[Account]):
    if not accounts:
        print_info("No accounts found. Create one to get started!")
        return

    if RICH_AVAILABLE:
        table = Table(title="Your Accounts", box=box.ROUNDED, border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="bold")
        table.add_column("Type", style="cyan")
        table.add_column("Currency")
        table.add_column("Balance", style="bold green", justify="right")
        table.add_column("Transactions", justify="right")

        total_balance = sum(a.balance for a in accounts)
        for i, acc in enumerate(accounts, 1):
            balance_style = "green" if acc.balance >= 0 else "red"
            table.add_row(
                str(i),
                acc.name,
                acc.account_type,
                acc.currency,
                f"[{balance_style}]${acc.balance:,.2f}[/{balance_style}]",
                str(len(acc.transactions)),
            )
        table.add_section()
        table.add_row("", "[bold]TOTAL[/bold]", "", "", f"[bold green]${total_balance:,.2f}[/bold green]", "")
        console.print(table)
    else:
        print("\n--- Your Accounts ---")
        for i, acc in enumerate(accounts, 1):
            print(f"{i}. {acc.name} | {acc.account_type} | ${acc.balance:,.2f} {acc.currency}")
        total = sum(a.balance for a in accounts)
        print(f"\nTotal: ${total:,.2f}")


def display_transactions(transactions: List[Transaction], title: str = "Transactions"):
    if not transactions:
        print_info("No transactions found.")
        return

    if RICH_AVAILABLE:
        table = Table(title=title, box=box.SIMPLE_HEAD, border_style="blue")
        table.add_column("Date", style="dim", width=12)
        table.add_column("Type", width=10)
        table.add_column("Category", style="cyan")
        table.add_column("Description")
        table.add_column("Amount", justify="right", style="bold")
        table.add_column("R", width=3)

        for t in transactions:
            if t.transaction_type == TransactionType.INCOME:
                amount_str = f"[green]+${t.amount:,.2f}[/green]"
                type_str = "[green]INCOME[/green]"
            else:
                amount_str = f"[red]-${t.amount:,.2f}[/red]"
                type_str = "[red]EXPENSE[/red]"
            recurring_icon = "🔄" if t.recurring else ""
            table.add_row(
                t.date.strftime("%Y-%m-%d"),
                type_str,
                t.category.value,
                t.description,
                amount_str,
                recurring_icon,
            )
        console.print(table)
    else:
        print(f"\n--- {title} ---")
        for t in transactions:
            print(str(t))


def display_budget_status(budget_statuses: List[Dict]):
    if not budget_statuses:
        print_info("No budgets configured.")
        return

    if RICH_AVAILABLE:
        table = Table(title="Budget Status", box=box.ROUNDED)
        table.add_column("Category", style="bold")
        table.add_column("Spent", justify="right")
        table.add_column("Limit", justify="right")
        table.add_column("Remaining", justify="right")
        table.add_column("Usage", justify="right")
        table.add_column("Status", width=10)

        for status in budget_statuses:
            cat = status["budget"].category.value
            spent = f"${status['spent']:,.2f}"
            limit = f"${status['limit']:,.2f}"

            if status["over_budget"]:
                remaining_str = f"[red]-${abs(status['remaining']):,.2f}[/red]"
                usage_str = f"[bold red]{status['usage_percent']:.0f}%[/bold red]"
                status_str = "[bold red]OVER[/bold red]"
            elif status["alert"]:
                remaining_str = f"[yellow]${status['remaining']:,.2f}[/yellow]"
                usage_str = f"[yellow]{status['usage_percent']:.0f}%[/yellow]"
                status_str = "[yellow]WARNING[/yellow]"
            else:
                remaining_str = f"[green]${status['remaining']:,.2f}[/green]"
                usage_str = f"[green]{status['usage_percent']:.0f}%[/green]"
                status_str = "[green]OK[/green]"

            table.add_row(cat, spent, limit, remaining_str, usage_str, status_str)
        console.print(table)
    else:
        print("\n--- Budget Status ---")
        for s in budget_statuses:
            cat = s["budget"].category.value
            pct = s["usage_percent"]
            status = "OVER" if s["over_budget"] else ("WARN" if s["alert"] else "OK")
            print(f"{cat}: ${s['spent']:.2f} / ${s['limit']:.2f} ({pct:.0f}%) [{status}]")


def display_savings_goals(goals: List[SavingsGoal]):
    if not goals:
        print_info("No savings goals set.")
        return

    if RICH_AVAILABLE:
        for goal in goals:
            bar_length = 30
            filled = int((goal.progress_percent / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            color = "green" if goal.is_complete else "yellow" if goal.progress_percent >= 50 else "red"
            text = Text()
            text.append(f"\n{goal.name}\n", style="bold")
            text.append(f"  [{bar}] ", style=color)
            text.append(f"{goal.progress_percent:.1f}%\n", style=f"bold {color}")
            text.append(f"  ${goal.current_amount:,.2f} of ${goal.target_amount:,.2f}", style="dim")
            if goal.deadline:
                days = goal.days_remaining()
                text.append(f"  |  {days} days left", style="dim")
            monthly = goal.monthly_savings_needed()
            if monthly:
                text.append(f"  |  ${monthly:,.2f}/mo needed", style="cyan")
            console.print(Panel(text, border_style=color, padding=(0, 2)))
    else:
        print("\n--- Savings Goals ---")
        for goal in goals:
            print(str(goal))


def display_monthly_report(report: Dict):
    if RICH_AVAILABLE:
        income = report["total_income"]
        expenses = report["total_expenses"]
        net = report["net_savings"]
        rate = report["savings_rate"]

        summary = (
            f"[bold]Period:[/bold] {report['period']}\n\n"
            f"[bold green]Income:[/bold green]   ${income:>10,.2f}\n"
            f"[bold red]Expenses:[/bold red]  ${expenses:>10,.2f}\n"
            f"{'─' * 26}\n"
            f"[bold]Net:[/bold]       ${net:>10,.2f}\n"
            f"[bold]Savings Rate:[/bold] {rate:.1f}%\n"
            f"[bold]Daily Avg:[/bold]   ${report['avg_daily_spending']:>9,.2f}\n"
            f"[bold]Balance:[/bold]    ${report['total_balance']:>10,.2f}"
        )
        console.print(Panel(summary, title="Monthly Report", border_style="cyan", padding=(1, 2)))

        if report["spending_by_category"]:
            table = Table(title="Spending by Category", box=box.SIMPLE_HEAD)
            table.add_column("Category", style="cyan")
            table.add_column("Amount", justify="right", style="red")
            table.add_column("% of Expenses", justify="right")
            for cat, amt in report["spending_by_category"].items():
                pct = (amt / expenses * 100) if expenses > 0 else 0
                table.add_row(cat.value, f"${amt:,.2f}", f"{pct:.1f}%")
            console.print(table)
    else:
        print(f"\n--- Report: {report['period']} ---")
        print(f"Income:   ${report['total_income']:,.2f}")
        print(f"Expenses: ${report['total_expenses']:,.2f}")
        print(f"Net:      ${report['net_savings']:,.2f}")
        print(f"Savings Rate: {report['savings_rate']:.1f}%")


def display_spending_trend(trend: List[Dict]):
    if RICH_AVAILABLE:
        table = Table(title="Spending Trend (Last 6 Months)", box=box.SIMPLE_HEAD)
        table.add_column("Month", style="bold")
        table.add_column("Income", justify="right", style="green")
        table.add_column("Expenses", justify="right", style="red")
        table.add_column("Net", justify="right")
        for entry in trend:
            net = entry["income"] - entry["expenses"]
            net_style = "green" if net >= 0 else "red"
            table.add_row(
                entry["label"],
                f"${entry['income']:,.2f}",
                f"${entry['expenses']:,.2f}",
                f"[{net_style}]${net:,.2f}[/{net_style}]",
            )
        console.print(table)
    else:
        print("\n--- Spending Trend ---")
        for entry in trend:
            net = entry["income"] - entry["expenses"]
            print(f"{entry['label']}: Income ${entry['income']:.2f} | Expenses ${entry['expenses']:.2f} | Net ${net:.2f}")


def prompt_menu(options: List[str], title: str = "Choose an option") -> int:
    print(f"\n{title}")
    for i, option in enumerate(options, 1):
        print(f"  [{i}] {option}")
    print(f"  [0] Back / Exit")
    while True:
        try:
            choice = input("\n> ").strip()
            val = int(choice)
            if 0 <= val <= len(options):
                return val
            print_error(f"Please enter a number between 0 and {len(options)}")
        except ValueError:
            print_error("Invalid input. Enter a number.")


def prompt_input(label: str, default: Optional[str] = None) -> str:
    if default:
        result = input(f"{label} [{default}]: ").strip()
        return result if result else default
    return input(f"{label}: ").strip()


def prompt_float(label: str, default: Optional[float] = None) -> float:
    while True:
        raw = prompt_input(label, str(default) if default is not None else None)
        try:
            return float(raw)
        except ValueError:
            print_error("Please enter a valid number.")


def prompt_confirm(message: str) -> bool:
    answer = input(f"{message} [y/N]: ").strip().lower()
    return answer in ("y", "yes")
