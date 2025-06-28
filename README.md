# Ancient-Poetry Name-Search

This project provides a small scaffold for working with the Chinese Poetry corpus. It focuses on building simple name search utilities over the ancient texts.

## Purpose

To demonstrate how to organise scripts and data for querying names within the classic poetry collections contained in this repository.

## Prerequisites

- Python 3.8 or later
- Packages listed in `requirements.txt`

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Basic Usage

Scripts and libraries will live under the `scripts/` and `lib/` directories. A basic search might look like:

```bash
python scripts/search.py --name "李白"
```

Results will be stored under the `index/` directory or printed to the console.
