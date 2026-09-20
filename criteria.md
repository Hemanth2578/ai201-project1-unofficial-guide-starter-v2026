# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

Four of my five questions have exactly one document that answers them, so there
is no excuse for missing those. The fifth asks what a wash costs in Morrow
House, and seven halls have laundry files that are word-for-word identical apart
from the price — that is the one I expect to be hard, which is why this is 4 of
5 and not 5 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

Every excerpt the model receives arrives labelled with its filename and the
grounding prompt tells it to name the file it used, so a missing source would
mean the model ignored a direct instruction rather than that the information was
not there. That is either working or it is not, so there is no reason to accept
four.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

Four of the five out-of-scope questions — Mongolia, diesel engines, the 1994
World Cup, Rust loops — share no subject matter with a corpus about student
life, so the gate should turn those away comfortably. The fifth asks about
ibuprofen dosage and my corpus has a health centre document, and that overlap is
the one I expect to slip through, which is why this is 4 of 5.

---

## 4. Something about your chunks

Every chunk is at least 150 characters long and includes the title line of the document it came from — in all 10 chunks I sample

**Why this target:**

Every document I read is a title line and two or three short paragraphs, so the
paragraph splitting I am likely to write in Milestone 3 would strand the title
in a chunk of its own — and the title is often the only place the topic word
appears, as in `study_group_rooms.txt`, which answers my whiteboard question
without ever saying "study room". 150 sits below the shortest document I read,
so anything under it is a fragment rather than a whole thought.

---

## 5. Your choice

Every answer the system gives names a file that contains the sentence the answer came from — in all 5 of my test questions that get answered rather than refused.

**Why this target:**

Criterion 2 passes as long as *any* filename shows up, so it cannot catch the
failure I actually expect: my corpus has families of near-identical files —
seven laundry documents, three per course — and with `TOP_K = 5` the model sees
several at once. No exceptions rather than 4 of 5 because a confident answer
pointing at the wrong file is worse than a refusal.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
