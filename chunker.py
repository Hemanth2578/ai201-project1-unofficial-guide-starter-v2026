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


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?



    MY STRATEGY: every document in `campus_life` is a title line followed by
    one to four short paragraphs, and the whole thing already reads as a single
    self-contained answer to a single question. The documents run 178 to 549
    characters, averaging 317. Nothing in the corpus is long enough to need
    cutting, so this keeps each document whole and deliberately does NOT split.

    That looks like the starter's behaviour and is not the same thing. The
    starter left documents whole by accident: `fallback_split` cuts blind at
    800 characters and simply never reached that limit here, so a longer
    document would have been sliced mid-sentence. This keeps them whole on
    purpose, and hands anything genuinely oversized to `fallback_split` rather
    than pretending the case cannot arise.

    Why not split on paragraphs, which is the obvious alternative: 56 of the 88
    documents have exactly two body paragraphs, so paragraph splitting would
    produce 183 chunks — and 93 of them, half, would fall under 150 characters
    even with the title line prepended. Half my chunks would be fragments. The
    second paragraph of a post is usually a related aside ("best time to do
    laundry here is Tuesday"), not a separate topic, and it costs little to
    leave it attached to the paragraph it qualifies.

    The trade-off I am accepting: a document covering two genuinely different
    topics — `health_center.txt` is walk-in hours AND counselling intake —
    stays as one chunk, so its embedding is an average of both. If retrieval
    misses on that kind of question, this is the cause, and splitting those
    specific documents is the fix to try in future.

    Chunks from the oversized path keep `chunker.py::fallback_split` as their
    provenance, so `app.py chunks` shows honestly which path produced what.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        text = doc.text.strip()
        if not text:
            continue

        # Safety valve. Never fires on campus_life (longest document is 549),
        # but it means the strategy degrades sensibly rather than emitting one
        # enormous chunk if a longer document is ever added.
        if len(text) > config.CHUNK_SIZE:
            chunks.extend(fallback_split([doc]))
            continue

        chunks.append(
            Chunk(
                text=text,
                source=doc.source,
                index=0,
                produced_by="chunker.py::split_documents",
            )
        )

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
