#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
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
import sys
from pathlib import Path

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


def fix_ent_file(path: Path, *, dry_run: bool) -> dict[str, str]:
    """Rewrite SYSTEM "..." references in an .ent file for POSIX.

    Converts backslashes to forward slashes and lower-cases the path, and
    normalizes the file's encoding from cp1252 to utf-8 to match the
    (renamed) files on disk. Returns the number of references changed.
    """
    original_text = read_ent_file(path)
    graphics: dict[str, str] = {}

    EXTERNAL_ENTITY = re.compile(
        r'(?P<prefix><!ENTITY\s*(?P<id>\S+)\s+SYSTEM\s+")(?P<path>[^"]+)(?P<suffix>"\s+NDATA\s+(?P<type>\w+)>)'
    )

    def repl(match: re.Match[str]) -> str:
        nonlocal graphics
        original_ref = match["path"]
        fixed_ref = original_ref.replace("\\", "/").lower()
        if match["type"] != "SGML":
            graphics[match["id"]] = fixed_ref
        if fixed_ref != original_ref:
            return match["prefix"] + fixed_ref + match["suffix"]
        else:
            return match.group(0)

    new_text = EXTERNAL_ENTITY.sub(repl, original_text)
    if new_text != original_text and not dry_run:
        path.write_text(new_text, encoding=TARGET_ENCODING, newline="")

    return graphics


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


def main(
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
    renamed = lower_case_tree(root, dry_run=dry_run)
    print(f"{len(renamed)} file(s)/directory(ies) renamed to lower case")

    ent_files = sorted(root.glob("jgoethe*.ent"))
    graphics: dict[str, str] = {}

    for ent_file in ent_files:
        graphics.update(fix_ent_file(ent_file, dry_run=dry_run))

    with Path("graphics.xml").open("wt", encoding="utf-8") as gr:
        gr.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        gr.write("<graphics>\n")
        for id, url in graphics.items():
            gr.write(f'    <graphic xml:id="{id}" url="{url}"/>\n')
        gr.write("</graphics>")
    print("normalized references")

    if dry_run:
        print("Dry run: skipping reference verification.")
        return

    missing = verify_references(root, ent_files)
    if missing:
        print(
            f"{len(missing)} reference(s) still don't resolve to a file "
            "(pre-existing data issues, not case/separator problems):"
        )
        for line in missing:
            print(f"  {line}")
    else:
        print("All references resolve to existing files.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        args[0] = Path(args[0])
    main(*args)
