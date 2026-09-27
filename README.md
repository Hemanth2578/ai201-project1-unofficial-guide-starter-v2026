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
| 1. Retrieved chunk contains the answer          | 4 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source                  | 5 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions           | 4 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks ≥150 chars and include the title line | 10 of 10 | 10/10 | 10/10 | 10/10 | MET     |
| 5. Named file contains the answer sentence      | 5 of 5   | 5/5   | 5/5   | 5/5   | MET     |

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

| #   | Criterion                                    | Verdict | How I decided |
| --- | -------------------------------------------- | ------- | ------------- |
| 1   | Retrieved chunks contain the answer          | MET     | Target was 4 of 5 and all three runs gave 5 of 5. Judged on the retrieved source list rather than `scorer.py::judge`, which measures the answer text instead — the two agree here but are different measurements. Reading the file is reading the chunk because all 88 chunks have `index == 0`: `split_documents` never splits, so a retrieved chunk is a whole document. |
| 2   | Every answer names a source                  | MET     | 15 of 15 answers across three runs named a file, so 5 of 5 every run against a 5-of-5 target. One gap I should name: all five questions passed the gate, so no refusal was produced, and `gate.REFUSAL` names no source. "Every answer" is therefore untested against refusals — not a miss, since the case never arose, but not proven either. |
| 3   | Gate stops out-of-corpus questions           | MET     | 5 of 5 refused against a 4-of-5 target, the widest margin of the five. The number is real but it is weak evidence: I chose the 0.6 cutoff in unit 1 by measuring these same five questions, so I tuned and tested on one set. It shows the cutoff separates these ten questions, not that it generalises. |
| 4   | Chunks ≥150 chars and include the title line | MET     | 10 of 10 in the sample, shortest 206 characters. I also checked all 88 rather than relying on a fixed slice: none under 150 (minimum 178) and every chunk opens with its title line. Holds as written and beyond it. |
| 5   | Named file contains the answer sentence      | MET     | 5 of 5 every run — but only because the model chose correctly, not because the criterion would have caught it otherwise. `housing_old_brewhouse_laundry.txt` also reads "$1.50 wash" and was in the retrieved set on all three runs, so naming it for a Morrow House question would have passed this criterion while being wrong. MET as written; revised in `criteria.md` to check the subject of the question, not a string. |

The verdict I checked hardest was criterion 5. Every criterion came out MET,
which means either the system is good or the targets were soft, so I argued the
opposite verdict on each one before writing it down. Four of those arguments
failed. The fifth did not: criterion 5 passed on a measurement that cannot
distinguish a correct answer from a lucky one, which is why it is revised in
`criteria.md` rather than simply recorded.

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

**I missed nothing.** All five criteria held on all three runs, so there is no
failure to trace to a stage. That is not the same as the system being excellent,
and my targets were set low. They were not all low in the same way, though, and
the way they were low is the finding.

### The pattern: I tested the system on the easy version of its job

Four of the five criteria were measured on material I chose after I had already
read the corpus. That is one problem, not four:

| # | Measured on                                                | Why that made it easy                                                                                                                                                                                                                  |
| - | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Five questions I wrote after reading the documents         | I knew where every answer lived, and the `expects` strings are short and distinctive (`$30`, `8am`, `210 and 211`). |
| 3 | The same five out-of-scope questions I used to pick 0.6    | I tuned the cutoff on this set in unit 1, then evaluated it on this set. Mongolia, diesel engines, the World Cup and Rust share nothing with student life; the nearest of them sits 0.225 above the cutoff.                              |
| 4 | Chunks from a corpus I knew was uniformly short            | The criterion asks whether documents stayed whole, and `split_documents` keeps documents whole by design. The shortest of all 88 is 178 characters. It could only fail if I changed the chunker or added a short document.             |
| 5 | The same five in-corpus questions as criterion 1           | Already revised in `criteria.md`: it checked for the presence of a string, which a wrong file could satisfy.                                                                                                                           |

Criterion 2 is the exception. It is genuinely binary and passed 15 of 15 on its
merits — but only against answers that got through the gate. No refusal was ever
produced, so it was never tested against `gate.REFUSAL`, which names no source.

### Where the risk actually sits, by stage

Nothing failed, but the evidence says which stages were never pushed:

- **Chunking** is untested where it is weakest. My chunker docstring names the
  trade-off I accepted: `health_center.txt` covers walk-in hours *and*
  counselling intake, so its embedding averages two topics. I asked about
  walk-in hours, the topic that leads the document. A counselling question
  would test the half the embedding is diluted on, and I did not ask one.
- **Retrieval** is strong on these questions rather than on the corpus. Every
  question returned its answer at rank 1 in unit 1, so tightening criterion 1
  from "the retrieved chunks include one" to "the top result contains it" would
  not bite. That tells me the softness is in the questions, not the threshold.
- **The gate** has never seen a question near the boundary. My own cutoff
  reasoning in unit 1 named the case I was worried about — a near-miss like
  "where is the nearest pharmacy" — and then none of my five out-of-scope
  questions came near it.

### The criterion I would tighten: 3

Criterion 3 cleared its target by the widest margin and rests on the weakest
evidence, because I set the cutoff and tested it on the same five questions.

> **Original:** When I ask a question my documents clearly don't cover, the
> relevance gate stops it — in at least 4 of 5 tries.
>
> **Tightened to:** The gate refuses at least 4 of 5 *boundary* questions —
> questions that borrow my corpus's vocabulary but that it cannot answer —
> written before I measure them, with the cutoff held at 0.6 and not re-tuned
> on them. For example: where the nearest pharmacy is; how to treat a sprained
> ankle; what the laundry costs in a hall that does not exist; when CHEM 101's
> midterm is (a course not in the corpus); what time a dining hall I made up
> opens.

I am keeping the target at 4 of 5 and changing the questions, because the number
was never the problem — the questions were far enough from the corpus that 0.6
could not miss. Every one of those five shares a word or a topic with a real
document (the health centre, the laundry files, the course and dining families),
which is the case a real student would hit and the case I never tested.

I have deliberately not run these yet. Setting a target after seeing whether it
passes is the thing unit 1 asked me not to do, so this stays a prediction: I
expect at least one of the five to slip through at 0.6, most likely the invented
hall's laundry price, because seven near-identical laundry documents will pull
it well inside the in-corpus range.

This is a tightening of a criterion I met, not a revision of one I missed, so
the original stays in `criteria.md` unchanged. The runner-up would be criterion
4, which is close to restating a chunking decision I had already made; I would
replace it with one that tests the two-topic trade-off above.

## The Improvement

**What I changed:** `chunker.py::split_documents` now splits a document into
one chunk per body paragraph, with the title line carried into each piece — but
only when every piece stays at or above 150 characters (`MIN_PIECE`). Otherwise
the document stays whole, exactly as in unit 1. On `campus_life` this splits 7 of
88 documents, giving 95 chunks instead of 88. Nothing else changed: same five
questions, same `TOP_K = 5`, same 0.6 cutoff, same prompt. The unit 1 index is
kept as variant `default` and the new one is variant `split`, so both exist at
once (`python app.py --variant split index`, then
`python run_eval.py --variant split --label after`).

**Why I picked it:** my diagnosis named `health_center.txt` as the place my
chunking was weakest — one embedding averaging walk-in hours with counselling
intake — and this is the smallest change that gives each topic its own embedding
without making the sub-150 fragments that made me reject paragraph splitting in
unit 1.

**What I predicted, written down before running it:**

1. The health question's best distance drops below 0.3321, because the walk-in
   chunk no longer averages in counselling.
2. All five criteria hold. `health_center.txt` is the only one of my five answer
   documents that splits; the other four stay whole.
3. Risk: the ibuprofen question gets closer than 0.844, because a pure health
   chunk is a better target for a medical question. Still refused.

**Why it might not work**, argued before running:

- Every criterion was already at its ceiling. The pass counts can only hold or
  fall, so they cannot show an improvement — if there is a benefit, it will only
  be visible in distance.
- Walk-in hours already lead the health document, so my question may not have
  been hurt much by the averaging. The half the averaging hurts most is
  counselling, and none of my questions asks about it.
- A split document can take two of the five top-k slots, pushing other documents
  out of what the model sees.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                                       | Target   | Run 1 | Run 2 | Run 3 | Verdict |
| ----------------------------------------------- | -------- | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer          | 4 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source                  | 5 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions           | 4 of 5   | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks ≥150 chars and include the title line | 10 of 10 | 10/10 | 10/10 | 10/10 | MET     |
| 5. Named file contains the answer sentence      | 5 of 5   | 5/5   | 5/5   | 5/5   | MET     |

Evidence: `results/run_2026-09-27_1246_after.md`, produced by `run_eval.py::main`
against index variant `split`, three runs, `cache=False`, 15 model calls. As
before, criteria 1, 3 and 4 do not involve a model call, so one measurement goes
in all three columns; criteria 2 and 5 read generated text.

#### Before and after, side by side

| Criterion                      | Target   | Before       | After        |
| ------------------------------ | -------- | ------------ | ------------ |
| 1. Retrieved chunk has answer  | 4 of 5   | 5/5 ×3 MET   | 5/5 ×3 MET   |
| 2. Every answer names a source | 5 of 5   | 5/5 ×3 MET   | 5/5 ×3 MET   |
| 3. Gate stops out-of-corpus    | 4 of 5   | 5/5 ×3 MET   | 5/5 ×3 MET   |
| 4. Chunks ≥150 + title line    | 10 of 10 | 10/10 ×3 MET | 10/10 ×3 MET |
| 5. Named file has the answer   | 5 of 5   | 5/5 ×3 MET   | 5/5 ×3 MET   |

The pass counts cannot tell the two apart, so the distances are where the change
shows. Best distance per question, from the two results files:

| Question                         | Before | After  | Change      |
| -------------------------------- | ------ | ------ | ----------- |
| Printing per semester            | 0.2749 | 0.2749 | none        |
| **Health centre walk-ins**       | 0.3321 | 0.2698 | **−0.0623** |
| Winter                           | 0.3900 | 0.3900 | none        |
| Whiteboard study rooms           | 0.3981 | 0.3981 | none        |
| Morrow House wash                | 0.2202 | 0.2202 | none        |
| _Out of scope:_ Mongolia         | 0.825  | 0.825  | none        |
| _Out of scope:_ diesel engine    | 0.934  | 0.934  | none        |
| _Out of scope:_ 1994 World Cup   | 0.886  | 0.886  | none        |
| _Out of scope:_ **ibuprofen**    | 0.844  | 0.849  | **+0.005**  |
| _Out of scope:_ Rust for loop    | 0.896  | 0.896  | none        |

#### Real output, after

**Criterion 1.** `health_center.txt` is now two chunks, so the unit 1 shortcut —
"a retrieved file is a retrieved chunk" — no longer holds for it. I checked
chunk text instead: for all five questions the answer is in the **rank 1**
chunk, both before and after. The two chunks `chunker.py::split_documents` now
makes from the health document:

```
--- health_center.txt#0 (192 chars) ---
The health centre

Walk-in hours are 8am to 11am; everything after that is by appointment and appointments run about a week out. If something is urgent, go at 8am and wait rather than booking.

--- health_center.txt#1 (185 chars) ---
The health centre

Counselling is separate, in the same building, and has its own intake process with a shorter wait than people expect — usually three or four days for a first session.
```

Rank 1 for the walk-in question is `#0`; `#1`, the counselling half, is rank 2.
From `run_eval.py::main`:

```
### At what time the health center open for walk-ins? — run 1

- Best distance: 0.2698 (passed the gate)
- Sources retrieved: dining_north_kitchen_followup.txt, dining_the_atrium_followup.txt, health_center.txt, study_library_hours.txt
```

Four sources, not five: the two health chunks take two of the five slots.

**Criterion 2.** 15 of 15 answers name a file. From
`generate.py::answer_from_chunks`:

```
### At what time the health center open for walk-ins? — run 1
The health centre is open for walk-ins from 8am to 11am (health_center.txt).

### At what time the health center open for walk-ins? — run 3
The health center is open for walk-ins from 8am to 11am (from health_center.txt).
```

**Criterion 3.** From `run_eval.py::check_out_of_scope`, cutoff 0.6:

```
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |
```

**Criterion 4.** From `chunker.py::describe`:

```
$ python chunker.py
95 chunks, 296 characters on average (shortest 152, longest 549), produced by chunker.py::split_documents
```

The `app.py chunks -n 10` sample passes 10 of 10, but it is a fixed slice and it
happened to miss all 14 of the new split chunks, so it says nothing about the
change. I checked all 95 instead: none under 150, and every one begins with its
own document's title line. The split rule guarantees this by construction — it
refuses any split that would break either half of the criterion.

**Criterion 5.** Every answer names the file for the hall or service asked
about, which passes both the original and the revised wording. From
`generate.py::answer_from_chunks`:

```
### How much does a wash cost in the Morrow House laundry room? — run 2
A wash costs $1.50 in the Morrow House laundry room.
Source: housing_morrow_house_laundry.txt (also mentioned in housing_morrow_house.txt)
```

`housing_old_brewhouse_laundry.txt`, also "$1.50 wash", is still in the
retrieved set at rank 3. This change was not aimed at that risk and did not move
it: the laundry question's top five are identical before and after.

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

**Partly, and not in a way my criteria can see.** It did what it was built to do,
and it moved none of my five numbers. Both are true.

- **The targeted retrieval improved.** The health question went from 0.3321 to
  0.2698. The walk-in chunk is a closer match on its own than it was averaged
  with counselling — prediction 1 held. I know the split caused this rather than
  noise because `health_center.txt` is the only answer document that split, and
  it is the only in-corpus distance that moved; the other four match to four
  decimal places.
- **No criterion moved.** All five were MET before and MET after. By the measure
  this unit grades, the change neither helped nor hurt — which is what I said
  would happen, because every target was already at its ceiling.
- **Prediction 3 was wrong.** I expected the ibuprofen question to move closer to
  the corpus. It moved away, 0.844 to 0.849. My best guess is that the unsplit
  health document read as a broader medical text than either half does alone,
  but I have not tested that; what I can say is that I predicted the wrong
  direction. It is the safe direction for the gate.
- **The cost I predicted showed up.** The split changed which documents were in
  the model's context for four of my five questions, though never the rank 1
  chunk. The health question's two chunks took ranks 1 and 2, pushing
  `dining_halden_hall_followup.txt` and `dining_the_ridgeway_cafe_followup.txt`
  out of the top five. On the printing question, the two halves of
  `money_textbooks.txt` took two slots and half of the newly split
  `course_engl_205_workload.txt` took a third, pushing out
  `admin_graduation_requirements.txt` and `course_cs_340.txt`. It was harmless
  here because every answer
  sat at rank 1. For a question whose answer sat at rank 4 or 5, this is the kind
  of crowding that could push it out.
- **It changed how I have to measure criterion 1.** With whole-document chunks I
  could judge criterion 1 from filenames. With split documents I have to read
  chunk text. Doing that exposed a second weakness in string matching: `$1.50`
  also matches `housing_aldridge_hall_laundry.txt`, whose wash costs $1.75 — the
  match is its _dry_ price. That is the same flaw I revised criterion 5 for.

**Would I keep it?** Yes, but I cannot prove it earns its place with these five
questions. The benefit is aimed at the counselling half of `health_center.txt`,
and none of my questions asks about counselling. That brings me back to my
Milestone 3 diagnosis: the soft part of this system is my questions, not my
pipeline. A test that could show this change working would need the question I
did not ask.

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
