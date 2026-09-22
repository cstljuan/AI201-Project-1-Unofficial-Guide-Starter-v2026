# The Unofficial Guide

Juan Castillo — `city_guides` corpus

---

# Unit 1

## What This Does

This is a retrieval-augmented question answering system over `city_guides`, a
corpus of fourteen travel guides covering nine towns in one fictional region
plus five guides that cut across all of them — eating, walking, regional
transport, seasons and accessibility. It answers practical questions of the
kind a visitor would actually ask: what time the pub at Elder Ness stops
serving food, how often the road out there floods, what it costs to climb the
church tower in Kestrelford.

Documents are split at their section headings, embedded locally with
`all-MiniLM-L6-v2`, and stored in Chroma. A question is embedded the same way,
the five nearest chunks are retrieved, and a relevance gate refuses outright if
the closest one is further than 0.6 away. Anything that passes the gate is
handed to `gemini-3.5-flash-lite` with an instruction to answer only from the
text provided and to name the file it used.

## Chunking Strategy

**Chunk size:** determined by `##` section boundaries, not a fixed number.
Observed range 172–758 characters across 94 chunks, averaging 318.
`CHUNK_SIZE = 800` is retained in `config.py` only as a safety ceiling.

**Overlap:** 0. Sections do not bleed into each other, so there is nothing for
an overlap to rescue.

I started on the shipped defaults — 800 characters with 120 of overlap — and
indexed once before changing anything, which is how I found the problem. Those
settings turned 14 documents into 51 chunks by counting characters and ignoring
the text completely. Two of the first three chunks I sampled began mid-word:
`guide_elder_ness.md#1` opened with "re is one car park" and
`guide_marchwood.md#3` with "d in smaller places", because the preceding chunk
had swallowed the first few characters of each word.

Reading the documents made the fix obvious. Every guide is divided into
labelled sections — getting there, getting around, where to eat, when to go —
and a section is already the unit a question gets asked about. Better still,
the longest section anywhere in the corpus is 709 characters, so splitting on
headings means every section fits inside one chunk and nothing needs cutting
twice.

The part I got wrong first time was the prefix. Splitting on `##` alone makes
each chunk worse, not better, and it took me a moment to see why: the body of
`guide_elder_ness.md`'s "Eat and drink" section never says "Elder Ness"
anywhere. The town name lives only in the `#` title at the top of the file. Cut
on headings without carrying that title down and every town's eating section
embeds to nearly the same place, so a question naming a town cannot pick
between them. Every chunk now opens with `Town — Section`, and the distance on
"What times does the pub at Elder Ness serve food?" is 0.169.

Result: 94 chunks, none beginning or ending mid-word.

## Sample Chunks

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#5` — produced by: `chunker.py::split_documents`

```
Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

**Chunk 3** — source: `guide_givens_mill.md#2` — produced by: `chunker.py::split_documents`

```
Givens Mill — Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.
```

**Chunk 4** — source: `guide_kestrelford.md#4` — produced by: `chunker.py::split_documents`

```
Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

**Chunk 5** — source: `guide_pellew_sands.md#6` — produced by: `chunker.py::split_documents`

```
Pellew Sands — When to go

June and September for the beach without the crowds. July and August are busy and the town is at its most itself, for better and worse. Winter is bleak, largely closed, and has a following among people who like that sort of thing.
```

Chunk 1 is a document preamble — the text above the first `##` heading — which
is why it carries a title and no section name. Ten of the 94 chunks are of that
shape; the other 84 open at a section heading.

## Sample Answer

**Question:** How much does it cost to climb the church tower in Kestrelford?

**Answer:**

```
  (best distance 0.406, cutoff 0.6)

It costs £2 to climb the church tower in Kestrelford (guide_kestrelford.md).

Sources retrieved: guide_kestrelford.md

1 model calls this session, 532 tokens (510 in, 22 out)
```

**My relevance cutoff:** 0.6, kept after measuring rather than inherited.

I ran all ten questions through `app.py retrieve`, which costs no model calls,
and recorded the best distance for each. The two groups separate completely.
My five in-corpus questions run 0.169 to 0.406. The five out-of-corpus ones run
0.808 to 0.982. Nothing at all lands between them, so the gap is 0.402 wide and
its midpoint is 0.607.

The shipped default of 0.6 sits almost exactly on that midpoint — 0.19 clear of
my hardest real question on one side, 0.20 clear of the nearest out-of-corpus
question on the other. I considered 0.65 for more headroom against a future
in-corpus question harder than any of my five, and 0.55 to bias towards
refusing, and kept 0.6 because I have no evidence that justifies moving it.
With a gap this wide, anything from roughly 0.45 to 0.75 would behave
identically on these ten questions, which says more about how far apart the
groups are than about the precision of the number.

| Question | In corpus? | Best distance |
|---|---|---|
| How much does it cost to climb the church tower in Kestrelford? | Yes | 0.406 |
| When did the railway line north of Brightwater close? | Yes | 0.258 |
| What times does the pub at Elder Ness serve food? | Yes | 0.169 |
| How often does the road to Elder Ness flood? | Yes | 0.264 |
| Where can I eat in Kestrelford on a Sunday evening? | Yes | 0.268 |
| What is the capital of Mongolia? | No | 0.808 |
| How do I change the oil in a diesel engine? | No | 0.881 |
| Who won the 1994 World Cup? | No | 0.982 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.835 |
| How do I write a for loop in Rust? | No | 0.859 |

## How I Used AI

**1.** I asked Claude to draft five test questions from my corpus, giving it
the documents to work from. It came back with five and an `expects` value for
each, and two needed changing. Its `expects` for the Elder Ness pub question
was just `"8"`, which would match almost any answer containing any number and
would have given me false passes the moment I built a scorer — I changed it to
`"6 to 8"`. I also had it annotate the fifth question, about eating in
Kestrelford on a Sunday evening, as the one I expected to fail, since the
answer genuinely requires two documents. That prediction turned out to be
wrong, which is the more interesting outcome and is recorded in criterion 1.

**2.** I asked Claude to implement the heading-aware chunker after I had
described the strategy. The implementation it produced split correctly on `##`
boundaries, but the thing worth recording is what it caught that I had not:
the section bodies never name their own town, so splitting on headings alone
would have made retrieval *worse* than the fixed-size chunker it replaced. The
`Town — Section` prefix came out of that, and it is the single change that most
affects my distances. I also added the oversized-section fallback after asking
what would happen on a corpus whose sections run longer than 800 characters —
nothing in `city_guides` triggers it, but without it the chunker silently emits
chunks of unbounded size.

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

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

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

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

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
