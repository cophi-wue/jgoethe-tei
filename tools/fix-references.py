#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cyclopts",
#     "rich",
# ]
# ///
"""Normalize the Windows/DOS-era file layout of this repository for POSIX.

The corpus was authored and packaged on Windows/DOS and shipped on a CD. The
``jgoethe*.ent`` files declare SGML entities pointing at auxiliary files
(images, sub-documents) using backslash path separators and whatever case the
author happened to type, relying on Windows' case-insensitive filesystem.
Several directories on disk were preserved in upper case (e.g. ``BILDER``,
``HEDERICH``) while the entity declarations reference them in lower or mixed
case. On a case-sensitive POSIX filesystem, that mismatch breaks every such
reference.

This script:

1. Renames every file/directory whose name is not already lower case to its
   lower-case form (deepest entries first, so directory renames don't orphan
   already-renamed children).
2. Rewrites ``SYSTEM "..."`` references in the ``jgoethe*.ent`` files to use
   forward slashes and lower case, so they resolve on POSIX.
3. Verifies that every rewritten reference now points at a file that exists.

Run it from anywhere; it defaults to operating on the repository that
contains this script.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import cyclopts
from rich.console import Console

app = cyclopts.App(help=__doc__)
console = Console()

SYSTEM_REF_RE = re.compile(r'(SYSTEM\s+")([^"]*)(")')
REPO_ROOT = Path(__file__).resolve().parent.parent


def is_git_tracked(root: Path) -> bool:
    return (root / ".git").exists()


def move(
    path: Path, new_path: Path, *, root: Path, use_git: bool, dry_run: bool
) -> None:
    if dry_run:
        return
    if use_git:
        result = subprocess.run(
            ["git", "mv", "--", str(path), str(new_path)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return
        # Not tracked by git (e.g. untracked file) - fall back to a plain rename.
    path.rename(new_path)


def lower_case_tree(root: Path, *, dry_run: bool) -> dict[str, str]:
    """Rename every file/directory under root whose name isn't already lower case.

    Processes deepest entries first so a directory rename never invalidates a
    path to one of its not-yet-renamed children. Returns a mapping of
    repo-relative POSIX paths, old -> new, for every renamed entry.
    """
    use_git = is_git_tracked(root)
    entries = sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True)

    renames: dict[str, str] = {}
    for path in entries:
        if ".git" in path.relative_to(root).parts:
            continue
        if path.name == path.name.lower():
            continue
        new_path = path.with_name(path.name.lower())
        if new_path.exists():
            raise FileExistsError(
                f"cannot rename {path} -> {new_path}: target already exists"
            )

        old_rel = path.relative_to(root).as_posix()
        move(path, new_path, root=root, use_git=use_git, dry_run=dry_run)
        new_rel = new_path.relative_to(root).as_posix()

        renames[old_rel] = new_rel
        console.print(f"  renamed [cyan]{old_rel}[/] -> [green]{new_rel}[/]")

    return renames


# The .ent files were authored on Windows in codepage 1252, so a handful of
# them embed literal accented characters (in SYSTEM paths and in prose
# comments) as single cp1252 bytes. The renamed files on disk are UTF-8
# encoded (this system's filesystem encoding), so a path reference has to be
# re-encoded to UTF-8, not just lower-cased, before it will resolve. Since a
# file can only have one encoding, fixing the paths means normalizing the
# whole file to UTF-8.
#
# That rewrite must stay idempotent: a file already normalized to UTF-8 must
# not be mistaken for cp1252 on a second run (every byte sequence UTF-8 can
# produce is either invalid or means something different in cp1252, so a
# strict UTF-8 decode is a reliable "already normalized" check).
SOURCE_ENCODING = "cp1252"
TARGET_ENCODING = "utf-8"


def read_ent_file(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode(TARGET_ENCODING)
    except UnicodeDecodeError:
        return raw.decode(SOURCE_ENCODING)


def fix_ent_file(path: Path, *, dry_run: bool) -> int:
    """Rewrite SYSTEM "..." references in an .ent file for POSIX.

    Converts backslashes to forward slashes and lower-cases the path, and
    normalizes the file's encoding from cp1252 to utf-8 to match the
    (renamed) files on disk. Returns the number of references changed.
    """
    original_text = read_ent_file(path)
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        original_ref = match.group(2)
        fixed_ref = original_ref.replace("\\", "/").lower()
        if fixed_ref != original_ref:
            changed += 1
        return f"{match.group(1)}{fixed_ref}{match.group(3)}"

    new_text = SYSTEM_REF_RE.sub(repl, original_text)
    if changed and not dry_run:
        path.write_text(new_text, encoding=TARGET_ENCODING, newline="")
    return changed


def verify_references(root: Path, ent_files: list[Path]) -> list[str]:
    """Return SYSTEM "..." references in ent_files that don't resolve to a file.

    A handful of references are broken in the source data itself (typos,
    scans that were apparently never delivered) independent of the
    Windows/POSIX case and separator issues this script fixes; those are
    reported here rather than treated as a failure of the normalization.
    """
    missing: list[str] = []
    for ent_file in ent_files:
        text = read_ent_file(ent_file)
        for match in SYSTEM_REF_RE.finditer(text):
            ref = match.group(2)
            if not (root / ref).exists():
                missing.append(f"{ent_file.name}: {ref}")
    return missing


@app.default
def main(
    *,
    root: Path = REPO_ROOT,
    dry_run: bool = False,
) -> None:
    """Normalize file names to lower case and fix Windows-style .ent references.

    Parameters
    ----------
    root:
        Repository root containing the jgoethe*.ent files and the directories
        they reference.
    dry_run:
        Show what would change without touching the file system.
    """
    console.print(f"[bold]Normalizing file names under {root}[/]")
    renamed = lower_case_tree(root, dry_run=dry_run)
    console.print(
        f"[bold]{len(renamed)}[/] file(s)/directory(ies) renamed to lower case\n"
    )

    ent_files = sorted(root.glob("jgoethe*.ent"))
    console.print(f"[bold]Fixing references in {len(ent_files)} .ent file(s)[/]")
    total_refs = 0
    for ent_file in ent_files:
        n = fix_ent_file(ent_file, dry_run=dry_run)
        if n:
            console.print(f"  {ent_file.name}: fixed {n} reference(s)")
        total_refs += n
    console.print(f"[bold]{total_refs}[/] reference(s) normalized\n")

    if dry_run:
        console.print("[yellow]Dry run: skipping reference verification.[/]")
        return

    missing = verify_references(root, ent_files)
    if missing:
        console.print(
            f"[yellow]{len(missing)} reference(s) still don't resolve to a file "
            "(pre-existing data issues, not case/separator problems):[/]"
        )
        for line in missing:
            console.print(f"  [yellow]{line}[/]")
    else:
        console.print("[green]All references resolve to existing files.[/]")


if __name__ == "__main__":
    app()
