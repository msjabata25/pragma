from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KnowledgeChunk:
    source: str        # e.g. "owasp/injection"
    heading: str       # the heading text that opened this section
    content: str       # full text of the section (heading + body)


def chunk_markdown(text: str, source: str) -> list[KnowledgeChunk]:
    """
    Split a markdown string into chunks at every ## or ### boundary.
    Sections with no meaningful body (< 30 chars after the heading) are skipped.
    """
    # Split at any line that starts with ## or ### (not ####+ — too granular)
    pattern = re.compile(r"^(#{2,3} .+)$", re.MULTILINE)
    splits   = list(pattern.finditer(text))

    if not splits:
        # No headings found — treat whole file as one chunk
        heading = Path(source).stem.replace("_", " ").title()
        return [KnowledgeChunk(source=source, heading=heading, content=text.strip())]

    chunks: list[KnowledgeChunk] = []

    # Text before the first heading — attach to filename as heading
    preamble = text[: splits[0].start()].strip()
    if len(preamble) >= 30:
        chunks.append(KnowledgeChunk(
            source=source,
            heading=Path(source).stem.replace("_", " ").title(),
            content=preamble,
        ))

    for i, match in enumerate(splits):
        start   = match.start()
        end     = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        section = text[start:end].strip()
        heading = match.group(1).lstrip("#").strip()
        body    = section[len(match.group(1)):].strip()

        if len(body) < 30:
            continue  # skip empty / near-empty sections

        chunks.append(KnowledgeChunk(source=source, heading=heading, content=section))

    return chunks


def chunk_file(path: Path, base_dir: Path) -> list[KnowledgeChunk]:
    """
    Read a .md file and chunk it.
    source is set to the path relative to base_dir, without extension.
    e.g.  sources/owasp/injection.md  →  "owasp/injection"
    """
    relative = path.relative_to(base_dir).with_suffix("")
    source   = relative.as_posix()
    text     = path.read_text(encoding="utf-8")
    return chunk_markdown(text, source)