from setuptools import setup, find_packages

setup(
    name="finance-tracker",
    version="1.0.0",
    description="A CLI personal finance tracker",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["rich>=13.0.0"],
    entry_points={
        "console_scripts": [
            "finance-tracker=finance_tracker.cli:main",
        ]
    },
)
