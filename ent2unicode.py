#!/usr/bin/env python3

import re
import sys
from pathlib import Path


def load_sgml_map(src=Path("SGML.TXT")) -> dict[str, int]:
    result = {}
    for entity_name, _, unicode in re.findall(
        r"^(\w+)\s+(\w+)\s+0x([0-9A-Za-z]+).*$", src.read_text(), re.MULTILINE
    ):
        result[entity_name] = int(unicode, 16)
    return result


def edit_ent(text: str, mapping: dict[str, int]) -> str:
    for name, codepoint in mapping.items():
        text = re.sub(rf"\[{name}\s*\]", f"&#{codepoint};", text)
    return text


def main():
    mapping = load_sgml_map(Path(sys.argv[0]).parent.joinpath("SGML.TXT"))
    for arg in sys.argv[1:]:
        file = Path(arg)
        src = file.read_text()
        fixed = edit_ent(src, mapping)
        if src != fixed:
            print(f"Rewrote entities in {file}")
            file.write_text(fixed)


if __name__ == "__main__":
    main()
