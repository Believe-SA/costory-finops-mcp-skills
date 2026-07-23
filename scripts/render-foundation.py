#!/usr/bin/env python3
"""Render shared FinOps knowledge fragments into managed blocks in skill files.

Single source of truth: knowledge/fragments/<id>.md
Targets: any plugins/costory/skills/**/*.md containing a managed block

    <!-- BEGIN foundation:<id> -->
    ...generated; do not edit by hand — edit knowledge/fragments/<id>.md...
    <!-- END foundation:<id> -->

This is how the repo keeps runtime-critical conventions DRY *without* breaking
SKILL.md self-containment (get_skill may not load references/): the canonical
text lives once under knowledge/, and is rendered inline into each skill that
needs it. Same managed-block pattern the Beads integration already uses.

Usage:
    scripts/render-foundation.py           # rewrite managed blocks in place
    scripts/render-foundation.py --check    # exit 1 if any block is stale (CI)

Dependencies: Python 3 stdlib only.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRAGMENTS = ROOT / "knowledge" / "fragments"
SKILLS = ROOT / "plugins" / "costory" / "skills"

# Capture a managed block and its id; the END marker must repeat the same id.
BLOCK = re.compile(
    r"<!-- BEGIN foundation:(?P<id>[a-z0-9-]+) -->\n"
    r".*?"
    r"\n<!-- END foundation:(?P=id) -->",
    re.DOTALL,
)


def fragment_text(fid: str) -> str:
    path = FRAGMENTS / f"{fid}.md"
    if not path.exists():
        sys.exit(
            f"ERROR: managed block references foundation:{fid} but there is no "
            f"source file {path.relative_to(ROOT)}"
        )
    return path.read_text(encoding="utf-8").strip("\n")


def rendered_block(fid: str) -> str:
    return (
        f"<!-- BEGIN foundation:{fid} -->\n"
        f"{fragment_text(fid)}\n"
        f"<!-- END foundation:{fid} -->"
    )


def process(path: pathlib.Path, check: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    new = BLOCK.sub(lambda m: rendered_block(m.group("id")), text)
    if new == text:
        return False
    rel = path.relative_to(ROOT)
    if check:
        print(f"STALE: {rel}")
    else:
        path.write_text(new, encoding="utf-8")
        print(f"rendered: {rel}")
    return True


def main() -> None:
    check = "--check" in sys.argv[1:]
    stale = [p for p in sorted(SKILLS.rglob("*.md")) if process(p, check)]
    if check:
        if stale:
            sys.exit(
                "Managed foundation blocks are out of date. "
                "Run scripts/render-foundation.py and commit the result."
            )
        print("All managed foundation blocks are up to date.")


if __name__ == "__main__":
    main()
