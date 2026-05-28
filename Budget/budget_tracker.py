# ============================================================
#  CodeOn Digital — UGX Budget Tracker
#  A simple command-line budget tracker in Ugandan Shillings
#  Author: [Your Name] | github.com/[your-username]
#  Built with Python 3 | No external libraries needed
# ============================================================

transactions = []

def display_banner():
    print("\n" + "=" * 50)
    print("       💰 UGX BUDGET TRACKER")
    print("       Built with Python | CodeOn Digital")
    print("=" * 50)

def format_ugx(amount):
    """Format a number as UGX currency."""
    return f"UGX {amount:,.0f}"

def add_income():
    print("\n--- ADD INCOME ---")
    description = input("Description (e.g. Salary, Freelance): ").strip()
    if not description:
        print("❌ Description cannot be empty.")
        return
    try:
        amount = float(input("Amount (UGX): ").strip())
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
        transactions.append({
            "type": "income",
            "description": description,
            "amount": amount
        })
        print(f"✅ Income added: {description} — {format_ugx(amount)}")
    except ValueError:
        print("❌ Please enter a valid number.")

def add_expense():
    print("\n--- ADD EXPENSE ---")
    description = input("Description (e.g. Transport, Food, Airtime): ").strip()
    if not description:
        print("❌ Description cannot be empty.")
        return
    try:
        amount = float(input("Amount (UGX): ").strip())
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
        transactions.append({
            "type": "expense",
            "description": description,
            "amount": amount
        })
        print(f"✅ Expense added: {description} — {format_ugx(amount)}")
    except ValueError:
        print("❌ Please enter a valid number.")

def view_summary():
    if not transactions:
        print("\n📭 No transactions yet. Add some income or expenses first.")
        return

    total_income  = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance       = total_income - total_expense

    print("\n" + "=" * 50)
    print("         📊 BUDGET SUMMARY")
    print("=" * 50)

    print("\n💚 INCOME")
    print("-" * 40)
    income_items = [t for t in transactions if t["type"] == "income"]
    if income_items:
        for t in income_items:
            print(f"  + {t['description']:<25} {format_ugx(t['amount']):>15}")
    else:
        print("  No income recorded.")

    print("\n🔴 EXPENSES")
    print("-" * 40)
    expense_items = [t for t in transactions if t["type"] == "expense"]
    if expense_items:
        for t in expense_items:
            print(f"  - {t['description']:<25} {format_ugx(t['amount']):>15}")
    else:
        print("  No expenses recorded.")

    print("\n" + "=" * 50)
    print(f"  Total Income:    {format_ugx(total_income):>25}")
    print(f"  Total Expenses:  {format_ugx(total_expense):>25}")
    print("-" * 50)

    if balance > 0:
        print(f"  ✅ Balance:      {format_ugx(balance):>25}  (You are saving!)")
    elif balance == 0:
        print(f"  ⚠️  Balance:      {format_ugx(balance):>25}  (Breaking even)")
    else:
        print(f"  ❌ Balance:      {format_ugx(balance):>25}  (Over budget!)")

    print("=" * 50)

def view_all_transactions():
    if not transactions:
        print("\n📭 No transactions recorded yet.")
        return

    print("\n" + "=" * 50)
    print("       📋 ALL TRANSACTIONS")
    print("=" * 50)
    for i, t in enumerate(transactions, 1):
        icon = "💚" if t["type"] == "income" else "🔴"
        print(f"  {i}. {icon} {t['description']:<22} {format_ugx(t['amount']):>15}")
    print("=" * 50)
    print(f"  Total transactions: {len(transactions)}")

def clear_all():
    confirm = input("\n⚠️  Are you sure you want to clear all transactions? (yes/no): ").strip().lower()
    if confirm == "yes":
        transactions.clear()
        print("✅ All transactions cleared.")
    else:
        print("❌ Cancelled.")

def savings_goal():
    print("\n--- 🎯 SAVINGS GOAL CHECKER ---")
    try:
        goal = float(input("Enter your savings goal (UGX): ").strip())
        if goal <= 0:
            print("❌ Goal must be greater than zero.")
            return
        total_income  = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        balance       = total_income - total_expense
        remaining     = goal - balance

        print(f"\n  Your goal:     {format_ugx(goal)}")
        print(f"  Current balance: {format_ugx(balance)}")

        if balance >= goal:
            print(f"  ✅ Goal reached! You have {format_ugx(balance - goal)} extra.")
        else:
            print(f"  ❌ You still need {format_ugx(remaining)} to reach your goal.")
            percentage = (balance / goal * 100) if goal > 0 else 0
            bar_filled = int(percentage / 5)
            bar        = "█" * bar_filled + "░" * (20 - bar_filled)
            print(f"  Progress: [{bar}] {percentage:.1f}%")
    except ValueError:
        print("❌ Please enter a valid number.")

def main():
    display_banner()
    print("\n  Track your income and expenses in Ugandan Shillings.")
    print("  Simple. Clear. Built for Uganda.\n")

    menu = {
        "1": ("Add Income",            add_income),
        "2": ("Add Expense",           add_expense),
        "3": ("View Summary",          view_summary),
        "4": ("View All Transactions", view_all_transactions),
        "5": ("Check Savings Goal",    savings_goal),
        "6": ("Clear All",             clear_all),
        "7": ("Exit",                  None),
    }

    while True:
        print("\n--- MENU ---")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")

        choice = input("\nChoose an option (1-7): ").strip()

        if choice == "7":
            print("\n👋 Goodbye! Keep tracking, keep saving.")
            print("   Built by CodeOn Digital — codeondigital.com\n")
            break
        elif choice in menu:
            _, action = menu[choice]
            action()
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
