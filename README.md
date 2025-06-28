# Ancient-Poetry Name-Search

This project provides a small scaffold for working with the Chinese Poetry corpus. It focuses on building simple name search utilities over the ancient texts.

## Installation

```bash
git clone https://github.com/kaiqizhang1120/chinese-poetry.git
cd chinese-poetry
pip install -r requirements.txt
```

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

## Usage

The following commands illustrate a typical workflow:

```bash
python scripts/preprocess.py --data-dir ./data --index-dir ./index
python scripts/search.py --char2 清 --char3 风 --tone2 2 --source poetry --distance adjacent
```

Expected output is similar to:

```text
西地锦 (ci)
寂寞悲秋怀抱。
掩重门悄悄。
\x1b[31m清\x1b[0m\x1b[31m风\x1b[0m皓月，朱阑画阁，双鸳池沼。
...
```

