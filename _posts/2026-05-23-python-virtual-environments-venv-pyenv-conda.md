---
layout: post
title: "Python Virtual Environments: venv, pyenv, and conda Compared"
date: "2026-05-23 00:00:00 +0530"
slug: python-virtual-environments-venv-pyenv-conda
description: "Understand when to use venv, pyenv, or conda for Python environment management, with practical commands for each tool and advice on combining them."
categories: ["Programming", "Tutorials"]
tags: ["python", "venv", "pyenv", "conda", "virtual environment", "dependency management", "tutorial", "macos", "linux"]
---

One of the first things that trips up Python developers — beginners and experienced alike — is environment management. Install a package globally and it might conflict with another project. Run the wrong Python version and half your dependencies break. Virtual environments are the solution, but Python has accumulated several tools for this, each solving a slightly different problem. Here's when to use each.

## The Problem They All Solve

Without isolation, all your projects share one Python installation and one set of packages. Project A needs `requests==2.28` and project B needs `requests==2.31` — you can't have both installed globally at the same time. Virtual environments create isolated sandboxes with their own site-packages so each project gets exactly what it needs.

## `venv` — Built-in, No Installation Required

`venv` is part of the Python standard library since 3.3. It creates a lightweight virtual environment that isolates packages from your global Python installation.

```bash
# create a virtual environment in .venv/
$ python3 -m venv .venv

# activate it
$ source .venv/bin/activate          # macOS/Linux
$ .venv\Scripts\activate             # Windows

# your shell prompt changes to show the active environment
(.venv) $ which python
/Users/mukul/myproject/.venv/bin/python

# install packages — they go into .venv, not global Python
(.venv) $ pip install fastapi uvicorn

# save dependencies
(.venv) $ pip freeze > requirements.txt

# deactivate when done
(.venv) $ deactivate
```

Always add `.venv/` to `.gitignore`. Commit `requirements.txt` instead.

**When to use `venv`**: for most Python projects where you're fine with whatever Python version is installed on the system.

## `pyenv` — Managing Multiple Python Versions

`venv` creates isolated package environments but it uses whatever `python3` points to on your system. If you need Python 3.10 for one project and 3.12 for another, `pyenv` is what you reach for.

```bash
# install pyenv (macOS)
$ brew install pyenv

# add to your shell profile
$ echo 'eval "$(pyenv init -)"' >> ~/.zshrc
$ source ~/.zshrc

# list available Python versions
$ pyenv install --list | grep "3.1"
  3.10.14
  3.11.9
  3.12.3
  3.13.0

# install a specific version
$ pyenv install 3.12.3
Downloading Python-3.12.3.tar.xz...
Installing Python-3.12.3...
Installed Python-3.12.3 to /Users/mukul/.pyenv/versions/3.12.3

# set a version for the current project (writes .python-version)
$ cd myproject
$ pyenv local 3.12.3

$ python --version
Python 3.12.3

# set global default
$ pyenv global 3.11.9
```

`pyenv` + `venv` together give you per-project Python version control AND package isolation — the combination most Python developers land on:

```bash
$ pyenv local 3.12.3
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

**When to use `pyenv`**: whenever you work across projects that require different Python versions.

## `conda` — Environments + Non-Python Dependencies

`conda` (from Anaconda/Miniconda) is a language-agnostic package manager. Unlike pip, it can install C libraries, CUDA drivers, R packages, and other non-Python dependencies. This makes it the standard tool in data science and machine learning.

```bash
# install miniconda (lighter than Anaconda)
$ brew install --cask miniconda

# create an environment with a specific Python version
$ conda create -n myenv python=3.11
$ conda activate myenv

(myenv) $ conda install numpy pandas scikit-learn
(myenv) $ conda install -c conda-forge xgboost

# save environment to a file
(myenv) $ conda env export > environment.yml

# recreate from file (on another machine)
$ conda env create -f environment.yml

# list all environments
$ conda env list
# conda environments:
#
base                     /opt/miniconda3
myenv               *    /opt/miniconda3/envs/myenv

# deactivate
(myenv) $ conda deactivate
```

You can still use `pip` inside a conda environment for packages not available on conda channels:

```bash
(myenv) $ pip install some-package-not-on-conda
```

**When to use `conda`**: for data science, ML, or any project needing non-Python binary dependencies (CUDA, OpenBLAS, etc.).

## Quick Comparison

| | `venv` | `pyenv` | `conda` |
|---|---|---|---|
| **Python versions** | Uses system Python | Manages multiple | Manages multiple |
| **Package isolation** | Yes | Needs venv too | Yes (built-in) |
| **Non-Python packages** | No | No | Yes |
| **Speed** | Fast | Fast | Slower |
| **Typical use** | Web/backend | Multi-version projects | Data science / ML |
| **Environment file** | `requirements.txt` | `.python-version` | `environment.yml` |

## Modern Alternative: `uv`

If you want a single fast tool that handles both Python version management and virtual environments, `uv` (from Astral, the Ruff team) is worth knowing:

```bash
$ brew install uv

# create a project with specific Python version
$ uv init myproject --python 3.12
$ cd myproject
$ uv add fastapi uvicorn

# run commands in the environment without activating
$ uv run python app.py
$ uv run pytest
```

`uv` is dramatically faster than pip for installs and is becoming popular as an all-in-one replacement for `pip` + `venv` + `pyenv` in non-conda workflows.

## Conclusion

`venv` is your default for simple projects. Add `pyenv` when you need to switch Python versions between projects. Reach for `conda` when your dependencies include compiled libraries outside the Python ecosystem. The combination of `pyenv` + `venv` covers the vast majority of backend and scripting work, while `conda` is nearly essential for data science. If you're starting fresh and want minimal friction, give `uv` a look — it's fast enough to make a real difference in day-to-day workflows.
