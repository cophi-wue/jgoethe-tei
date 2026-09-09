#!/usr/bin/env python3
"""Apply the corrections listed in JGKO1130.rtf to jgoethe.xml.

The RTF is a hand-written errata list from 1998. Most entries have the
shape

    <id> [<id> ...] [[P]] <alt> –> <neu>

where <id> refers to the numeric suffix of an ``xml:id="JG<id>"``
element in jgoethe.xml. Those entries are simple, literal text
substitutions and are applied automatically, scoped to the named
element(s).

Everything else - missing links, wrongly tagged speakers, paragraph
marks or line breaks to delete, new entries to add, and so on - needs
an editorial decision about *how* to change the markup and is only
reported, never touched automatically.
"""

from __future__ import annotations

import argparse
import bisect
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# RTF destinations whose text must never leak into the document body.
SUPPRESS_DESTINATIONS = {
    "fonttbl",
    "colortbl",
    "stylesheet",
    "info",
    "header",
    "footer",
    "footnote",
    "pict",
    "object",
}

CHAR_ESCAPES = {
    "endash": "–",
    "emdash": "—",
    "bullet": "•",
    "lquote": "‘",
    "rquote": "’",
    "ldblquote": "“",
    "rdblquote": "”",
    "tab": "\t",
    "line": "\n",
}


@dataclass
class Run:
    italic: bool
    text: str


@dataclass
class Paragraph:
    runs: list[Run] = field(default_factory=list)
    has_unresolved_unicode: bool = False

    @property
    def plain_text(self) -> str:
        return "".join(r.text for r in self.runs if not r.italic)

    @property
    def note_text(self) -> str:
        return "".join(r.text for r in self.runs if r.italic).strip()


@dataclass
class _GroupState:
    italic: bool = False
    suppress: bool = False
    just_opened: bool = True
    uc: int = 1


def parse_rtf_paragraphs(raw: str) -> list[Paragraph]:
    """Minimal RTF tokenizer, good enough for this one document.

    Tracks brace-nested formatting/destination state so that italic
    "editorial note" text can be told apart from the plain text of an
    entry, and so metadata groups (font/colour/style tables, document
    info, header) never contribute text.
    """
    paragraphs = [Paragraph()]
    stack = [_GroupState()]
    pending_uc_skip = 0
    i = 0
    n = len(raw)

    def emit(text: str) -> None:
        nonlocal pending_uc_skip
        if pending_uc_skip > 0:
            pending_uc_skip -= 1
            return
        state = stack[-1]
        if state.suppress or not text:
            return
        paragraphs[-1].runs.append(Run(italic=state.italic, text=text))

    while i < n:
        c = raw[i]
        if c == "{":
            stack.append(
                _GroupState(italic=stack[-1].italic, suppress=stack[-1].suppress)
            )
            i += 1
            continue
        if c == "}":
            if len(stack) > 1:
                stack.pop()
            i += 1
            continue
        if c == "\\":
            i += 1
            if i >= n:
                break
            if raw[i] == "'":
                byte = int(raw[i + 1 : i + 3], 16)
                stack[-1].just_opened = False
                char = bytes([byte]).decode("cp1252", errors="replace")
                if char == "�":
                    paragraphs[-1].has_unresolved_unicode = True
                emit(char)
                i += 3
                continue
            if raw[i].isalpha():
                j = i
                while j < n and raw[j].isalpha():
                    j += 1
                word = raw[i:j]
                k = j
                if k < n and raw[k] == "-":
                    k += 1
                num_start = k
                while k < n and raw[k].isdigit():
                    k += 1
                param = raw[num_start:k] if k > num_start else None
                if k < n and raw[k] == " ":
                    k += 1
                i = k

                state = stack[-1]
                if state.just_opened and word in SUPPRESS_DESTINATIONS:
                    state.suppress = True
                state.just_opened = False

                if word == "par":
                    if not state.suppress:
                        paragraphs.append(Paragraph())
                elif word == "i":
                    state.italic = param != "0"
                elif word == "plain":
                    state.italic = False
                elif word == "uc":
                    state.uc = int(param) if param else 1
                elif word == "u":
                    pending_uc_skip += state.uc
                    paragraphs[-1].has_unresolved_unicode = True
                elif word in CHAR_ESCAPES:
                    emit(CHAR_ESCAPES[word])
                continue
            # control symbol, e.g. \{ \} \\ \*
            sym = raw[i]
            i += 1
            state = stack[-1]
            if state.just_opened and sym == "*":
                state.suppress = True
            state.just_opened = False
            if sym in "{}\\":
                emit(sym)
            continue
        j = i
        while j < n and raw[j] not in "\\{}":
            j += 1
        text = raw[i:j]
        if text:
            stack[-1].just_opened = False
        emit(text)
        i = j

    return paragraphs


ARROW_RE = re.compile(r"\s*–\s*>\s*")


@dataclass
class Entry:
    ids: list[int]
    is_p: bool
    old: str | None
    new: str | None
    note: str
    raw: str
    skip_reason: str | None = None

    @property
    def actionable(self) -> bool:
        return self.skip_reason is None and bool(self.ids) and self.old is not None


def parse_entries(paragraphs: list[Paragraph]) -> list[Entry]:
    entries: list[Entry] = []
    for para in paragraphs:
        text = para.plain_text.strip()
        if not text:
            continue
        text = text.lstrip("*").strip()

        tokens = text.split()
        ids: list[int] = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.isdigit():
                ids.append(int(tok))
                i += 1
            elif tok == "und" and i + 1 < len(tokens) and tokens[i + 1].isdigit():
                i += 1
            else:
                break
        rest = " ".join(tokens[i:])

        is_p = False
        if rest.startswith("[P]"):
            is_p = True
            rest = rest[3:].strip()

        if not ids:
            entries.append(
                Entry(
                    ids=[], is_p=is_p, old=None, new=None, note=para.note_text, raw=text
                )
            )
            continue

        m = ARROW_RE.search(rest)
        if not m:
            entries.append(
                Entry(
                    ids=ids,
                    is_p=is_p,
                    old=None,
                    new=None,
                    note=para.note_text,
                    raw=text,
                )
            )
            continue

        old = rest[: m.start()].strip()
        new = rest[m.end() :].strip()
        # A handful of entries only re-case the first letter by mistake
        # (e.g. "Kornmt -> kommt", clearly meant to stay "Kommt" at the
        # start of a sentence). When alt/neu start with the same letter
        # in different case, keep alt's case rather than trust a typo.
        if (
            old
            and new
            and old[0].isalpha()
            and new[0].isalpha()
            and old[0].lower() == new[0].lower()
            and old[0] != new[0]
        ):
            new = old[0] + new[1:]
        skip_reason = None
        if para.has_unresolved_unicode:
            skip_reason = "enthaelt nicht dekodierbares RTF-Unicode-Escape (\\u)"
        elif not old or not new:
            skip_reason = "alt- oder neu-Text nach dem Pfeil ist leer"
        elif old == new:
            skip_reason = "alt- und neu-Text sind identisch"
        elif any(ch in old + new for ch in "<>&"):
            skip_reason = "alt/neu-Text enthaelt XML-Sonderzeichen (<, >, &)"

        entries.append(
            Entry(
                ids=ids,
                is_p=is_p,
                old=old,
                new=new,
                note=para.note_text,
                raw=text,
                skip_reason=skip_reason,
            )
        )
    return entries


def load_entries(rtf_path: Path) -> list[Entry]:
    raw = rtf_path.read_text(encoding="cp1252")
    # The original document is missing a paragraph break between two
    # entries here ("...eine36803 M\'e4nnnen...", jointly meaning
    # "36349 oino -> eine" and "36803 M\"annnen -> M\"annern").
    raw = raw.replace(
        "eine36803 M\\'e4nnnen \\endash > M\\'e4nnern",
        "eine\\par 36803 M\\'e4nnnen \\endash > M\\'e4nnern",
    )
    paragraphs = parse_rtf_paragraphs(raw)
    return parse_entries(paragraphs)


# --- Applying entries to jgoethe.xml -------------------------------------
#
# The numeric ids in the errata do NOT reliably match today's
# xml:id="JG<n>" values: the errata itself says so ("bleibt, bis ein
# Ausgleich bei der Eintragszaehlung konstruiert werden kann") and
# spot checks confirm it - the drift grows through the document
# (three later SGML/P4/P5 conversions happened after 1998). So ids are
# only used for logging, never to locate text.
#
# Instead each (alt, neu) pair is looked up by its literal, word-
# bounded text in a *tag-free projection* of the whole document (so a
# word split across inline markup, e.g. "Michaelis</ref>Mosaisches",
# still matches "MichaelisMosaisches"). Because both the errata list
# and jgoethe.xml preserve the book's reading order, the k-th id listed
# for a given (alt, neu) pair is paired with the k-th matching
# occurrence in the file. A fix is only applied when the number of
# occurrences found matches the number of ids requested - anything
# else is reported for manual resolution instead of guessed at.
#
# A match is turned into raw-text edits via a character-level diff
# between alt and neu: unchanged stretches are left alone, and only
# the actually-changed characters are touched. If a changed stretch
# straddles a markup boundary (i.e. deleting/replacing it would also
# delete a tag), the whole correction is refused automatically.

ID_POS_RE = re.compile(r'xml:id="JG(\d+)"')
TAG_RE = re.compile(r"(<[^>]*>)")


def build_id_index(text: str) -> tuple[list[int], list[int]]:
    positions: list[int] = []
    ids: list[int] = []
    for m in ID_POS_RE.finditer(text):
        positions.append(m.start())
        ids.append(int(m.group(1)))
    return positions, ids


def nearest_id(positions: list[int], ids: list[int], pos: int) -> int | None:
    i = bisect.bisect_right(positions, pos) - 1
    return ids[i] if i >= 0 else None


@dataclass
class Projection:
    text: str
    run_starts: list[int]
    run_raw_starts: list[int]

    def to_raw(self, proj_index: int) -> int:
        i = bisect.bisect_right(self.run_starts, proj_index) - 1
        return self.run_raw_starts[i] + (proj_index - self.run_starts[i])


def build_projection(xml_text: str) -> Projection:
    """A view of xml_text with all tags removed, plus an offset map back."""
    pieces: list[str] = []
    run_starts: list[int] = []
    run_raw_starts: list[int] = []
    proj_pos = 0
    raw_pos = 0
    for idx, piece in enumerate(TAG_RE.split(xml_text)):
        if idx % 2 == 1:  # this piece is a matched tag
            raw_pos += len(piece)
            continue
        if piece:
            run_starts.append(proj_pos)
            run_raw_starts.append(raw_pos)
            pieces.append(piece)
            proj_pos += len(piece)
            raw_pos += len(piece)
    return Projection("".join(pieces), run_starts, run_raw_starts)


def word_bounded_pattern(old: str) -> re.Pattern[str]:
    prefix = r"(?<!\w)" if old[0].isalnum() else ""
    suffix = r"(?!\w)" if old[-1].isalnum() else ""
    return re.compile(prefix + re.escape(old) + suffix)


@dataclass
class RawEdit:
    id_: int
    near_id: int | None
    old: str
    new: str
    start: int
    end: int
    replacement: str


def diff_to_raw_edits(
    proj: Projection, proj_start: int, old: str, new: str, id_: int, near_id: int | None
) -> list[RawEdit] | None:
    """Character-diff old->new and map the changed spans back to raw offsets.

    Returns None if a changed span is not backed by a contiguous raw run
    (i.e. it would have to delete part of a tag).
    """
    edits: list[RawEdit] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if i1 < i2:
            raw_start = proj.to_raw(proj_start + i1)
            raw_end = proj.to_raw(proj_start + i2 - 1) + 1
            if raw_end - raw_start != i2 - i1:
                return None  # a tag is embedded in the span to be changed
        else:
            # pure insertion: place it right before the next kept
            # character (or right after the previous one at the end).
            if proj_start + i1 < proj_start + len(old):
                raw_start = raw_end = proj.to_raw(proj_start + i1)
            else:
                raw_start = raw_end = proj.to_raw(proj_start + i1 - 1) + 1
        edits.append(
            RawEdit(
                id_=id_,
                near_id=near_id,
                old=old,
                new=new,
                start=raw_start,
                end=raw_end,
                replacement=new[j1:j2],
            )
        )
    return edits


def build_edits(entries: list[Entry], xml_text: str, log: list[str]) -> list[RawEdit]:
    id_positions, id_values = build_id_index(xml_text)
    proj = build_projection(xml_text)

    groups: dict[tuple[str, str], list[int]] = {}
    for entry in entries:
        if not entry.actionable:
            continue
        assert entry.old is not None and entry.new is not None
        groups.setdefault((entry.old, entry.new), []).extend(entry.ids)

    edits: list[RawEdit] = []
    for (old, new), ids in groups.items():
        occurrences = [m.start() for m in word_bounded_pattern(old).finditer(proj.text)]
        if len(occurrences) != len(ids):
            id_list = ", ".join(f"JG{i}" for i in ids)
            log.append(
                f"UEBERSPRUNGEN '{old}' -> '{new}': {len(ids)} Fundstelle(n) erwartet "
                f"(ids {id_list}), aber {len(occurrences)} Vorkommen von "
                f"'{old}' im Dokument gefunden"
            )
            continue
        for id_, proj_start in zip(ids, occurrences):
            near_id = nearest_id(id_positions, id_values, proj.to_raw(proj_start))
            new_edits = diff_to_raw_edits(proj, proj_start, old, new, id_, near_id)
            if new_edits is None:
                log.append(
                    f"UEBERSPRUNGEN JG{id_} (nahe JG{near_id}): '{old}' -> '{new}' "
                    "aendert Text, der von Markup unterbrochen wird, manuelle Pruefung noetig"
                )
                continue
            edits.extend(new_edits)

    edits.sort(key=lambda e: e.start)

    # Guard against overlapping edits (should not happen, but two
    # corrections could in principle claim overlapping text).
    kept: list[RawEdit] = []
    for edit in edits:
        if kept and edit.start < kept[-1].end:
            log.append(
                f"UEBERSPRUNGEN JG{edit.id_} ('{edit.old}' -> '{edit.new}'): "
                "ueberlappt mit einer anderen Korrekturstelle, manuelle Pruefung noetig"
            )
            continue
        kept.append(edit)
    return kept


def apply_edits(xml_text: str, edits: list[RawEdit]) -> str:
    pieces: list[str] = []
    pos = 0
    for edit in edits:
        pieces.append(xml_text[pos : edit.start])
        pieces.append(edit.replacement)
        pos = edit.end
    pieces.append(xml_text[pos:])
    return "".join(pieces)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent.parent
    parser.add_argument("--rtf", type=Path, default=root / "JGKO1130.rtf")
    parser.add_argument("--xml", type=Path, default=root / "jgoethe.xml")
    parser.add_argument(
        "--report", type=Path, default=root / "tools" / "errata_report.txt"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur berichten, jgoethe.xml nicht schreiben.",
    )
    args = parser.parse_args()

    entries = load_entries(args.rtf)
    xml_text = args.xml.read_text(encoding="utf-8")

    log: list[str] = []
    edits = build_edits(entries, xml_text, log)

    applied = len({(e.id_, e.old, e.new) for e in edits})
    informational = [e for e in entries if not e.ids]
    non_actionable = [e for e in entries if e.ids and not e.actionable]

    if not args.dry_run and edits:
        new_text = apply_edits(xml_text, edits)
        args.xml.write_text(new_text, encoding="utf-8")

    report_lines = [
        f"Eintraege insgesamt (RTF-Absaetze mit Inhalt): {len(entries)}",
        f"Automatisch angewandte Einzelkorrekturen:      {applied}",
        f"Textstellen dabei veraendert:                   {len(edits)}",
        f"Nicht anwendbar / manuelle Pruefung noetig:     {len(non_actionable)}",
        f"Rein informativ (keine xml:id-Referenz):        {len(informational)}",
        "",
        "--- uebersprungene id-Zuordnungen ---",
        *log,
        "",
        "--- Eintraege, die redaktionelle Entscheidungen brauchen (mit xml:id) ---",
    ]
    for e in non_actionable:
        ids = " ".join(f"JG{i}" for i in e.ids)
        reason = e.skip_reason or "kein 'alt -> neu'-Muster erkannt"
        note = f" [{e.note}]" if e.note else ""
        report_lines.append(f"{ids}: {e.raw!r} -- {reason}{note}")

    report_lines.append("")
    report_lines.append(
        "--- rein informative Eintraege (Ueberschriften o.ae., keine id) ---"
    )
    for e in informational:
        note = f" [{e.note}]" if e.note else ""
        report_lines.append(f"{e.raw!r}{note}")

    report = "\n".join(report_lines) + "\n"
    args.report.write_text(report, encoding="utf-8")

    print(
        f"{applied} Korrekturen angewandt ({len(edits)} Textstellen).", file=sys.stderr
    )
    print(f"Bericht geschrieben nach {args.report}", file=sys.stderr)
    if args.dry_run:
        print("Dry-Run: jgoethe.xml wurde NICHT veraendert.", file=sys.stderr)


if __name__ == "__main__":
    main()
