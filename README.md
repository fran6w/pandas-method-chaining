# pandas-method-chaining

`pandas-method-chaining` is a plugin for `flake8` that provides *method chaining* linting for `pandas` code.

It is a fork from [pandas-vet](https://github.com/deppen8/pandas-vet). The global framework of `pandas-vet` has been reused. All rules have been fully rewritten and adapted to pandas *method chaining*, except the one dealing with the use of `inplace=True`.

## Motivation

The source of motivation is to help `pandas` users to write *method chaining* code style.

Why a fork? The original `pandas-vet` includes rules which don't deal with *method chaining*, and some of them are not compatible with this style (e.g. PD005 and PD006 using operators instead of methods).

A source of inspiration was [Matt Harrisson's](https://twitter.com/__mharrison__) book [Effective Pandas](https://hairysun.com/announcing-effective-pandas.html).

## Limits

- False positives may occur: e.g., either non `pandas` statements matching the rules, or intentional style of the programmer.
- Output messages could be improved: e.g., either too general, or not adapted to specific cases.

## Installation

`pandas-method-chaining` is a plugin for `flake8`. If you don't have `flake8` already, it will install automatically when you install `pandas-method-chaining`.

For the moment, the plugin is on **github** only and can be installed, in a dedicated environment, after cloning the repo by:

```bash
$ pip install -e .
```

When this plugin meets its users, it will be added to **PyPI** to ease the installation.

## Usage

Once installed successfully in an environment that also has `flake8` installed, `pandas-method-chaining` should run using:

```bash
$ flake8 python_script.py --select=PMC
```

## Contributors

### Contributors from `pandas-vet`

- https://github.com/deppen8/pandas-vet#contributors

### Other contributor

- fran6w

## List of warnings

Except `PMC001` which uses a *should*, other warnings use a *could*.

**PMC001** usage of `inplace=True` should be avoided

**PMC002** reassignment using call could be replaced by method chaining

**PMC003** reassignment using subscript could be replaced by method chaining

**PMC004** assignment using subscript could be replaced by `assign()`

**PMC005** assignment using attribute could be replaced by `assign()`

**PMC006** assignment of index or columns could be replaced by `rename()`

**PMC007** selection reusing a variable could be performed with a `lambda`
