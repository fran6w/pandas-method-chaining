from setuptools import setup

requires = ["flake8 > 3.0.0", "attr"]

flake8_entry_point = "flake8.extension"

long_description = """
A flake8 style checker for pandas method chaining, forked from https://github.com/deppen8/pandas-vet]
"""

setup(
    name="pandas-method-chaining",
    version="0.1.0",
    author="Francis Wolinski",
    license="MIT",
    description="A pandas method chaining checker",
    install_requires=requires,
    entry_points={
        flake8_entry_point: [
            "PMC=pandas_method_chaining:Plugin",
        ]
    }
)
