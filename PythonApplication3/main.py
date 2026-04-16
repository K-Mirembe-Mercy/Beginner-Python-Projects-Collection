"""
main.py - Entry point for the Personal Finance Tracker.
"""

import sys
import os
import argparse

# Allow running as `python main.py` from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from finance_tracker.cli import FinanceCLI


def main():
    parser = argparse.ArgumentParser(
        description="Personal Finance Tracker — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --data-dir ~/my_finances
        """,
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store data files (default: ./data)",
    )
    args = parser.parse_args()
    app = FinanceCLI(data_dir=args.data_dir)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
