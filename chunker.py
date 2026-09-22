"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _split_title(text: str) -> tuple[str, str]:
    """
    Pull the `# Title` line off the top of a document.

    Returns (title, the rest). If there is no `# ` line, the title comes back
    empty and the text is unchanged.
    """
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return lines[0][2:].strip(), "\n".join(lines[1:]).strip()
    return "", text.strip()


def _sections(text: str) -> list[tuple[str, str]]:
    """
    Break a document into (heading, body) pairs on its `## ` lines.

    Whatever sits before the first `## ` comes back as ("", preamble), so the
    introduction to each guide is kept rather than thrown away. A document with
    no `## ` lines at all comes back as one ("", whole text) pair, which is why
    this is safe to run over a corpus that isn't structured this way.
    """
    parts = re.split(r"^## +", text, flags=re.MULTILINE)

    sections = [("", parts[0].strip())]
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        sections.append((heading.strip(), body.strip()))

    return [(heading, body) for heading, body in sections if body]


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split each document at its `## ` section headings.

    Why headings and not a character count: every document in `city_guides` is
    divided into labelled sections — getting there, getting around, where to
    eat — and the longest of those sections in the whole corpus is 709
    characters, comfortably inside one chunk. A section is already the unit a
    question gets asked about, so cutting anywhere else only does damage. The
    fixed-size chunker this replaces was splitting mid-word.

    Every chunk is prefixed with its document title and section heading:

        Elder Ness — Eat and drink

        One pub, serving food 12 to 2 and 6 to 8, closed Mondays...

    That prefix is not decoration. The body of that section never says "Elder
    Ness" anywhere — the town name lives only in the `# ` title at the top of
    the file. Without the prefix, every town's eating section embeds to
    almost the same place and a question naming a town can't pick between
    them.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        title, body = _split_title(doc.text)
        if not title:
            title = doc.source.rsplit(".", 1)[0].replace("_", " ")

        index = 0
        for heading, section in _sections(body):
            header = f"{title} — {heading}" if heading else title
            text = f"{header}\n\n{section}"

            # Nothing in city_guides reaches this, but a section longer than
            # CHUNK_SIZE would otherwise sail through as one oversized chunk.
            # Fall back to fixed-size windows for that section alone, keeping
            # the header on every piece so each one still names its town.
            if len(text) > config.CHUNK_SIZE:
                room = config.CHUNK_SIZE - len(header) - 2
                pieces = fallback_split(
                    [Document(source=doc.source, text=section)],
                    chunk_size=room,
                    overlap=min(config.CHUNK_OVERLAP, room // 2),
                )
                bodies = [p.text for p in pieces]
            else:
                bodies = [section]

            for piece in bodies:
                chunks.append(
                    Chunk(
                        text=f"{header}\n\n{piece}",
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
