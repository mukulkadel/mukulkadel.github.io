---
layout: post
title: "Python Scripts That Save Hours: File and Directory Processing Patterns"
date: "2026-09-02 00:00:00 +0530"
slug: python-file-processing-automation-scripts
description: "Practical Python patterns for automating file and directory tasks, using pathlib, shutil, and glob to replace repetitive manual work."
categories: ["Programming", "Tutorials"]
tags: ["python", "scripting", "automation", "file processing", "pathlib", "shutil", "glob", "batch processing", "productivity"]
---

If you've ever manually renamed fifty files, hunted through nested folders for duplicates, or copy-pasted the same "move these into dated subfolders" routine more than twice, that's a script, not a chore. Python's standard library — `pathlib`, `shutil`, and `glob` — covers almost every file and directory task you'd otherwise do by hand, and none of it requires a third-party package. Let's go through the patterns that come up constantly.

## Finding Files: `pathlib` and Glob Patterns

`pathlib.Path` is the modern, object-oriented way to work with filesystem paths in Python, and it makes recursive file discovery a one-liner.

```python
from pathlib import Path

downloads = Path.home() / "Downloads"

for pdf in downloads.glob("*.pdf"):
    print(pdf.name)
```

```
$ python find_pdfs.py
invoice_march.pdf
report_draft.pdf
receipt_2026.pdf
```

`glob("*.pdf")` only searches the immediate directory; `rglob("*.pdf")` searches recursively through every subdirectory, which is usually what you actually want when hunting for files scattered across nested folders.

```python
for pdf in downloads.rglob("*.pdf"):
    print(pdf.relative_to(downloads))
```

```
invoice_march.pdf
2025/receipt_2026.pdf
2025/archive/report_draft.pdf
```

## Batch Renaming Files

Manually renaming dozens of files with a shared pattern — stripping a prefix, adding a date, fixing inconsistent casing — is exactly the kind of task that takes ten minutes by hand and ten seconds as a script.

```python
from pathlib import Path
import re

photos = Path("photos")

for photo in photos.glob("IMG_*.jpg"):
    # IMG_20260315_142233.jpg -> 2026-03-15-142233.jpg
    match = re.match(r"IMG_(\d{4})(\d{2})(\d{2})_(\d+)\.jpg", photo.name)
    if match:
        year, month, day, time = match.groups()
        new_name = f"{year}-{month}-{day}-{time}.jpg"
        photo.rename(photo.with_name(new_name))
        print(f"{photo.name} -> {new_name}")
```

```
$ python rename_photos.py
IMG_20260315_142233.jpg -> 2026-03-15-142233.jpg
IMG_20260316_091205.jpg -> 2026-03-16-091205.jpg
```

`Path.rename()` operates on the path object directly, and `with_name()` builds a new path in the same directory with a different filename — no manual string concatenation of directory and filename needed.

## Organizing Files into Dated Subfolders

A common pattern for a downloads or screenshots folder: automatically sort files into subfolders by their modification date.

```python
from pathlib import Path
from datetime import datetime
import shutil

source = Path("screenshots")

for file in source.iterdir():
    if file.is_file():
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        dest_dir = source / mod_time.strftime("%Y-%m")
        dest_dir.mkdir(exist_ok=True)
        shutil.move(str(file), dest_dir / file.name)
```

```
$ ls screenshots/
2026-01/  2026-02/  2026-03/
$ ls screenshots/2026-03/
Screenshot_20260305.png  Screenshot_20260312.png
```

`mkdir(exist_ok=True)` avoids an exception if the destination folder already exists from a previous run — important for a script you expect to run repeatedly rather than once.

## Finding and Removing Duplicate Files

Duplicate detection by filename is unreliable — the real signal is content. Hashing each file's contents and grouping by hash finds true duplicates regardless of naming.

```python
import hashlib
from pathlib import Path
from collections import defaultdict

def file_hash(path: Path, chunk_size: int = 8192) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

files_by_hash = defaultdict(list)
for file in Path("documents").rglob("*"):
    if file.is_file():
        files_by_hash[file_hash(file)].append(file)

for file_hash_value, paths in files_by_hash.items():
    if len(paths) > 1:
        print(f"Duplicate set: {[str(p) for p in paths]}")
```

```
$ python find_duplicates.py
Duplicate set: ['documents/report.pdf', 'documents/backup/report.pdf']
```

Reading in fixed-size chunks (`f.read(chunk_size)`, looping with the walrus operator until it returns empty) keeps memory usage constant regardless of file size — hashing a 4GB file this way uses the same memory as hashing a 4KB one, since the file is never loaded into memory all at once.

## Bulk Text Processing Across Many Files

Searching and replacing text across a directory of files — updating a copyright year, fixing a broken import path — is another task that's error-prone by hand and trivial as a script.

```python
from pathlib import Path

def replace_in_file(path: Path, old: str, new: str) -> bool:
    content = path.read_text()
    if old not in content:
        return False
    path.write_text(content.replace(old, new))
    return True

changed = []
for py_file in Path("src").rglob("*.py"):
    if replace_in_file(py_file, "import config", "from app import config"):
        changed.append(py_file)

print(f"Updated {len(changed)} files")
for f in changed:
    print(f"  {f}")
```

```
$ python bulk_replace.py
Updated 3 files
  src/handlers/auth.py
  src/handlers/users.py
  src/main.py
```

Checking `if old not in content` before writing avoids rewriting files that don't need changes, which both saves I/O and keeps file modification timestamps accurate for files that were genuinely untouched.

## Safe Cleanup: Dry-Run Before You Delete

Any script that deletes files should support a dry-run mode first — the cost of testing a deletion script wrong is much higher than testing a read-only one wrong.

```python
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--execute", action="store_true", help="Actually delete files")
args = parser.parse_args()

old_logs = [f for f in Path("logs").glob("*.log") if f.stat().st_size == 0]

for log in old_logs:
    if args.execute:
        log.unlink()
        print(f"Deleted: {log}")
    else:
        print(f"Would delete: {log}")
```

```
$ python cleanup_logs.py
Would delete: logs/2026-01-03.log
Would delete: logs/2026-01-04.log

$ python cleanup_logs.py --execute
Deleted: logs/2026-01-03.log
Deleted: logs/2026-01-04.log
```

Defaulting to dry-run and requiring an explicit `--execute` flag means running the script by accident (or re-running it out of habit) never destroys anything — the destructive path has to be opted into deliberately, every time.

## Conclusion

`pathlib` for finding and manipulating paths, `shutil` for moving and copying, and content hashing for genuine duplicate detection cover the overwhelming majority of file-processing automation you'll actually need. The pattern worth internalizing across all of these examples is defensive by default: check before you write, dry-run before you delete, and use `mkdir(exist_ok=True)` so scripts are safe to re-run. Once a task like this has been done manually twice, it's worth the ten minutes to write the script — you'll run it more than twice.
