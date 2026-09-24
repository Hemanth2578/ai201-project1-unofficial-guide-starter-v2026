# The Unofficial Guide

Hemanth Gorla — corpus: `campus_life`

---

# Unit 1

## What This Does

I built this over `campus_life`, 88 short posts about student life — dorms,
dining halls, courses, the admin rules nobody explains. Ask it something
specific and it finds the right documents and answers from those alone, naming
the file. Ask what a wash costs in Morrow House and you get $1.50. Ask the
capital of Mongolia and it tells you it doesn't know.

## Chunking Strategy

**Chunk size:** No fixed window — one document is one chunk. An 800-character
ceiling sits in `split_documents` as a safety valve, but it never fires on this
corpus.

**Overlap:** None. Nothing is split, so there is nothing to overlap.

I picked `campus_life`, and the first thing `python app.py index` told me was
that the starter's 800-character window never cut anything: 88 documents in, 88
chunks out. The documents run 178 to 549 characters, averaging 317. That isn't
a bug and it isn't nothing — for these documents, one post already is one
chunk. The question Milestone 3 actually put to me was whether to leave it that
way.

Reading the documents, each one is a title line followed by one to four short
paragraphs, and the whole thing reads as a single self-contained answer to a
single question. `admin_add_drop_deadline.txt` is three facts about one
deadline. `course_hist_118_workload.txt` is the reading load for one course and
nothing else. Cutting either of those makes both halves worse.

So I kept documents whole — but deliberately rather than by accident, which is
the part that matters. The starter left them whole by luck: `fallback_split`
cuts blind at 800 characters and simply never reached that limit here, so a
longer document would have been sliced mid-sentence. My `split_documents`
emits one chunk per document on purpose and hands anything over 800 characters
to `fallback_split` instead of pretending the case cannot arise. Same output on
this corpus, different behaviour on any other.

**Why not split on paragraphs**, which was the obvious alternative: I measured
it before writing any code. 56 of my 88 documents have exactly two body
paragraphs, so paragraph splitting would produce 183 chunks — and 93 of them,
half, would fall under 150 characters even with the title line prepended. Half
my chunks would be fragments, which fails my own acceptance criterion 4. The
second paragraph of a post is usually a related aside ("best time to do laundry
here is Tuesday or Wednesday morning"), not a separate topic, and it costs
little to leave it attached to what it qualifies.

**What I found afterwards, having already decided.** Printing five chunks and
reading them turned up a case my rule handles badly.
`housing_innisfree_hall.txt` covers six things in one chunk — build dates, room
layout, the good, no air conditioning, laundry prices and noise — so its
embedding is an average of all six and it matches every housing question a
little and none of them well. Checking how widespread that is: 14 files mention
a wash price, because every hall summary repeats the price already given in its
own `_laundry` file. About 16 of my 88 documents have this shape — 7 hall
summaries and 9 course summaries — each duplicating content from dedicated
sibling files.

I did not change my numbers, because the other ~72 documents genuinely are one
thought each and re-chunking all of them to fix 16 would make the common case
worse. But it is a real cost and I would rather name it than discover it in the
run log: if a housing or course question retrieves badly in unit 2, this is the
cause, and the fix to try is splitting only `housing_*.txt` and `course_*.txt`
on their paragraph breaks while leaving everything else whole.

## Sample Chunks

**Chunk 1** — source: admin_add_drop_deadline.txt#0 `— produced by: chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: course_biol_160.txt#0 `— produced by: chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: course_hist_118_workload.txt#0 `— produced by: chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: dining_pellew_dining_hall_followup.txt#0 `— produced by: chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: housing_innisfree_hall.txt#0 `— produced by: chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** How much does a wash cost in the Morrow House laundry room?

**Answer:**

```
  (best distance 0.220, cutoff 0.6)

A wash costs $1.50 in the Morrow House laundry room.

Source: housing_morrow_house_laundry.txt (also found in housing_morrow_house.txt)

Sources retrieved: housing_aldridge_hall_laundry.txt, housing_innisfree_hall_laundry.txt, housing_morrow_house.txt, housing_morrow_house_laundry.txt, housing_old_brewhouse_laundry.txt

1 model calls this session, 745 tokens (704 in, 41 out)
```

I picked this question deliberately because it is the hardest one I have. Seven
halls each have a laundry file and the files are word-for-word identical apart
from the price, so three wrong-hall chunks (Aldridge, Innisfree, Old Brewhouse)
were in the model's context alongside the right one. It still answered $1.50,
which is Morrow's price and not any of theirs, and it named the file the figure
came from rather than a plausible-looking sibling. It also noticed on its own
that the same price appears in `housing_morrow_house.txt` — which is true, and
is the duplication between hall summaries and their `_laundry` files that I
wrote about under Chunking Strategy.

**My relevance cutoff:** 0.6

I kept the starter's number, but only after measuring — it is the middle of the
range my own data supports, not an inherited default. My five in-corpus
questions ran 0.220 to 0.398 and the five out-of-scope questions ran 0.825 to
0.934. That is a gap of 0.427 with nothing in it, so any cutoff between about
0.45 and 0.75 would separate the two groups perfectly on these ten questions.
0.6 sits near the middle of that window, leaving 0.202 of margin above my worst
real question and 0.225 below my nearest out-of-scope one.

What I would get wrong at 0.6: I wrote my five in-corpus questions after
reading the documents, so I already knew what the answers were and where they
sat — which makes them easier than questions asked cold. A vaguer question from
someone who had not read the corpus could land at 0.65 and be
refused even though the answer is sitting in the corpus. Moving to 0.7 would
catch those and still refuse all five out-of-scope questions, but it spends most
of the safety margin — a near-miss like "where is the nearest pharmacy" would
get through and be answered from thin material. I would rather refuse a few real
questions than answer one I shouldn't, so I stayed at 0.6.

I left `TOP_K` at 5. All five in-corpus questions return the correct document at
rank 1, not rank 3 or 5, so widening retrieval would add loosely related
material without finding anything new.

| Question                                                    | In corpus? | Best distance |
| ----------------------------------------------------------- | ---------- | ------------- |
| How much does a wash cost in the Morrow House laundry room? | Yes        | 0.220         |
| How much printing does each student get per semester?       | Yes        | 0.275         |
| At what time the health center open for walk-ins?           | Yes        | 0.332         |
| How's winter actually feels like in the campus?             | Yes        | 0.390         |
| Which study rooms have white boards?                        | Yes        | 0.398         |
| What is the capital of Mongolia?                            | No         | 0.825         |
| What is the recommended dosage of ibuprofen for a headache? | No         | 0.844         |
| Who won the 1994 World Cup?                                 | No         | 0.886         |
| How do I write a for loop in Rust?                          | No         | 0.896         |
| How do I change the oil in a diesel engine?                 | No         | 0.934         |

## How I Used AI

**1.** I described my approach, one post per chunk, and had Claude write
`split_documents` from it. It added an 800-character fallback for anything too
long to keep whole. I kept that, and had it record in the docstring why I turned
down paragraph splitting.

**2.** I also used it to check my five questions against the corpus, polish the
wording, and run the similarity scores. Then I had it tighten the grounding
prompt so a document that only mentions the topic, without answering, returns
"I don't have enough information" instead of a guess.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                                       | Target   | Run 1 | Run 2 | Run 3 | Verdict |
| ----------------------------------------------- | -------- | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer          | 4 of 5   | 5/5   | 5/5   | 5/5   |         |
| 2. Every answer names a source                  | 5 of 5   | 5/5   | 5/5   | 5/5   |         |
| 3. Gate stops out-of-corpus questions           | 4 of 5   | 5/5   | 5/5   | 5/5   |         |
| 4. Chunks ≥150 chars and include the title line | 10 of 10 | 10/10 | 10/10 | 10/10 |         |
| 5. Named file contains the answer sentence      | 5 of 5   | 5/5   | 5/5   | 5/5   |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

Criteria 1, 3 and 4 are deterministic. `split_documents` keeps each document
whole, so a retrieved chunk is a source file and criterion 1 is a property of
retrieval alone; criterion 3 is a comparison against a fixed cutoff; criterion 4
measures the chunks themselves. None involves a model call, so one measurement
goes in all three columns. Criteria 2 and 5 both read generated text, so they
are the two that could have moved between runs — `run_eval.py::run_once` passes
`cache=False`, and the three answers per question differ in wording, which is
the evidence the runs were real.

### Criterion 1 — retrieved chunks contain the answer

Produced by `store.py::search` over chunks from `chunker.py::split_documents`,
logged by `run_eval.py::main`. Judged on the retrieved source list, not on the
generated answer: `scorer.py::judge` checks whether the _answer text_ contains
the expected string, which is a different measurement.

Because `split_documents` keeps every document whole, a retrieved chunk **is** a
source file, so "the retrieved chunks contain the answer" is checkable by
reading the files that came back.

| Question                                                    | Answer lives in                    | In the retrieved sources? |
| ----------------------------------------------------------- | ---------------------------------- | ------------------------- |
| How much printing does each student get per semester?       | `admin_printing_quota.txt`         | ✅                        |
| At what time the health center open for walk-ins?           | `health_center.txt`                | ✅                        |
| How's winter actually feels like in the campus?             | `winter_gear.txt`                  | ✅                        |
| Which study rooms have white boards?                        | `study_group_rooms.txt`            | ✅                        |
| How much does a wash cost in the Morrow House laundry room? | `housing_morrow_house_laundry.txt` | ✅                        |

**5 of 5.** The hard case was the laundry question — seven halls have
word-for-word identical laundry files apart from the price — and retrieval
returned the right one at rank 1 (best distance 0.2202, the closest of all five).

Real output, the laundry question, run 1:

```
### How much does a wash cost in the Morrow House laundry room? — run 1

- Best distance: 0.2202 (passed the gate)
- Sources retrieved: housing_aldridge_hall_laundry.txt, housing_innisfree_hall_laundry.txt, housing_morrow_house.txt, housing_morrow_house_laundry.txt, housing_old_brewhouse_laundry.txt
```

`housing_morrow_house_laundry.txt`, from the corpus, contains the answer:

```
Laundry in Morrow House

Machines take $1.50 wash, $1.25 dry, coin or card. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.
```

Three of the four other retrieved files are sibling laundry documents, which is
the failure mode I predicted in criterion 1's "why this target" — it did not
happen, but the near-misses were in the context window.

This criterion does not vary between runs. Retrieval is deterministic and no
model call is involved, so the same number goes in all three run columns.

---

### Criterion 2 — every answer names a source

Produced by `generate.py::answer_from_chunks`, called from `run_eval.py::run_once`
with `cache=False`.

**5 of 5 on all three runs**, 15 answers out of 15. Two runs of the same question,
to show the wording changed while the source naming held:

```
### At what time the health center open for walk-ins? — run 1

The health centre is open for walk-ins from 8am to 11am. (Source: health_center.txt)
```

```
### At what time the health center open for walk-ins? — run 3

The health center's walk-in hours are from 8am to 11am (health_center.txt).
```

The model varies where it puts the filename — inline parentheses, a trailing
`Source:` line, or both — but it never omitted it. A third question, showing the
trailing-line form:

```
### How much printing does each student get per semester? — run 2

Each student gets $30 of printing per semester.

Source: admin_printing_quota.txt
```

This is the only one of the five criteria that reads generated text, so it is the
only one that could have moved between runs. It didn't.

---

### Criterion 3 — the relevance gate stops out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, gate logic in `gate.py::check`,
cutoff 0.6.

```
## The relevance gate on out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.6. Refused 5 of 5.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |
```

**5 of 5.** The ibuprofen question is the one I expected to slip through,
because my corpus has a health centre document. It came back at 0.844 — the
second-closest of the five to my corpus — so the overlap I predicted is real
and shows up in the numbers. It was never close to crossing, though: 0.244 of
margin above the 0.6 cutoff.

Retrieval is deterministic and the gate is a comparison against a fixed number,
so one pass is the whole measurement and the same number goes in all three
run columns.

---

### Criterion 4 — every chunk is ≥150 characters and includes its title line

Produced by `app.py::cmd_chunks` over chunks from `chunker.py::split_documents`
(`python app.py chunks -n 10`, an even spread across all 88 chunks).

| #   | Chunk                                | Characters | Title line present                   |
| --- | ------------------------------------ | ---------- | ------------------------------------ |
| 1   | `admin_add_drop_deadline.txt#0`      | 300        | ✅ "On the add/drop deadline"        |
| 2   | `admin_meal_plan_changes.txt#0`      | 222        | ✅ "On the meal plan changes"        |
| 3   | `advising_registration.txt#0`        | 292        | ✅ "Registration and your adviser"   |
| 4   | `course_cs_340_exams.txt#0`          | 206        | ✅ "CS 340 Databases — assessment"   |
| 5   | `course_hist_118.txt#0`              | 400        | ✅ "HIST 118 Modern World History"   |
| 6   | `course_phys_130_workload.txt#0`     | 237        | ✅ "Workload for PHYS 130 Mechanics" |
| 7   | `dining_north_kitchen.txt#0`         | 344        | ✅ "North Kitchen"                   |
| 8   | `dining_verrill_street_grill.txt#0`  | 409        | ✅ "Verrill Street Grill"            |
| 9   | `housing_calder_annexe_noise.txt#0`  | 286        | ✅ "Noise levels in Calder Annexe"   |
| 10  | `housing_morrow_house_laundry.txt#0` | 301        | ✅ "Laundry in Morrow House"         |

**10 of 10.** Shortest sampled chunk is 206 characters, 56 above the 150 floor.

Corroborated across the whole corpus by `chunker.py::describe`:

```
$ py chunker.py
88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::split_documents
```

The corpus minimum of 178 is above 150, so no chunk anywhere fails the length
half — the sample is consistent with the full set rather than a lucky draw.

The shortest sampled chunk in full, as real output:

```
======================================================================
Chunk 4  |  source: course_cs_340_exams.txt#0  |  produced by: chunker.py::split_documents
======================================================================
CS 340 Databases — assessment

One midterm and a final, both open-book. Lightly curved, usually two or three points.

Start the term project in week three, not week eight; everyone learns this the hard way.
```

This criterion does not vary between runs. `split_documents` reads the corpus off
disk and emits one chunk per document; no model call is involved.

---

### Criterion 5 — the named file contains the sentence the answer came from

Produced by `generate.py::answer_from_chunks`; verified by reading each named
file in `corpora/campus_life/documents/`.

| Question                                                    | File the answer named              | Contains the answer sentence?                        |
| ----------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------- |
| How much printing does each student get per semester?       | `admin_printing_quota.txt`         | ✅ "Every student gets $30 of printing per semester" |
| At what time the health center open for walk-ins?           | `health_center.txt`                | ✅ "Walk-in hours are 8am to 11am"                   |
| How's winter actually feels like in the campus?             | `winter_gear.txt`                  | ✅ "Cold from mid-November to early March"           |
| Which study rooms have white boards?                        | `study_group_rooms.txt`            | ✅ "Rooms 210 and 211 have whiteboards"              |
| How much does a wash cost in the Morrow House laundry room? | `housing_morrow_house_laundry.txt` | ✅ "Machines take $1.50 wash"                        |

**5 of 5 on all three runs.** The laundry question in full, which is the one this
criterion was written for:

```
### How much does a wash cost in the Morrow House laundry room? — run 3

A wash costs $1.50 in the Morrow House laundry room.

Source: housing_morrow_house_laundry.txt (also mentioned in housing_morrow_house.txt)
```

The file it named, from the corpus:

```
Laundry in Morrow House

Machines take $1.50 wash, $1.25 dry, coin or card. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.
```

The second file it volunteers, `housing_morrow_house.txt`, also carries the $1.50
figure — that is the hall-summary/`_laundry` duplication I wrote about under
Chunking Strategy, and the model spotted it unprompted rather than being asked.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
