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

This work continues the same Unit 1 fork: https://github.com/cstljuan/ai201-project1-unofficial-guide-starter-v2026.
The original criteria and questions were committed in `00290f6`, before the heading-aware chunker in `54dd83b` and the Unit 1 write-up in `5e9663f`. All Unit 1 content and commits are preserved. `criteria.md` and `questions.py` are unchanged.

## Run Log - Before

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | Every answer (5 of 5 in-scope questions) | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk word boundaries and section starts | No mid-word boundaries; at least 4 of 5 sampled chunks start at a section heading | 0 violations; 4/5 | 0 violations; 4/5 | 0 violations; 4/5 | MET |
| 5. Sources named contain the fact | At least 4 of 5 questions | 5/5 | 5/5 | 5/5 | MET |

The gate was measured once on the original five `OUT_OF_SCOPE` questions because retrieval and the fixed cutoff are deterministic. Criterion 4 was also measured once: all 94 chunk bodies were checked against their original document word boundaries, and the same five sample labels printed in Unit 1 were used, including the preamble. A section start means the existing title/section prefix corresponds to a source `##` heading, not that the output retains Markdown heading syntax. The deterministic values are repeated in the three columns.

Criterion 2 uses the five generated in-scope answers, as specified by its Unit 1 rationale ("All five"). Gate refusals are measured separately in criterion 3 and intentionally have no fabricated citation. The literal phrase "Every answer" is broader than that rationale; next time I would make this scope explicit.

No `scorer.py` exists. These are manual judgments of the saved answers and chunks, not fabricated automated pass labels. For criterion 1, Q1 requires the tower fee, Q2 the railway closure year, Q3 both pub service windows, Q4 the annual flood frequency, and Q5 the Kestrelford evening window plus the Sunday caveat and regional exceptions. For criterion 5, I checked the fact in the named document, not just whether a retrieved filename appeared.

| Question | Retrieved fact, each run | Names source, runs 1/2/3 | Factual citation, runs 1/2/3 | Supporting retrieved chunk |
|---|---|---|---|---|
| Tower fee | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_kestrelford.md#4` |
| Railway closure | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_regional_transport.md#0` |
| Elder Ness pub hours | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_elder_ness.md#3` |
| Elder Ness floods | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_elder_ness.md#1` |
| Kestrelford Sunday evening | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_eating.md#1` |

The last row measures the original retrieval and attribution criteria, not a guarantee that Sunday dining is available. The source explicitly says Sunday evening is difficult, and gives general hours without confirming Sunday opening.

### Actual baseline outputs

**Criterion 1:** retrieved by `store.py::search`, produced by `chunker.py::split_documents`, Q1 run 1, `guide_kestrelford.md#4`:

```text
Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

**Criterion 2:** generated by `generate.py::answer_from_chunks` through `run_eval.py::run_once`, Q1 run 1:

```text
It costs £2 to climb the church tower in Kestrelford (guide_kestrelford.md).
```

**Criterion 3:** `run_eval.py::check_out_of_scope` calls `store.py::search` and `gate.py::check`; the returned text is `gate.py::REFUSAL`:

| Question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.808364 | refused |
| How do I change the oil in a diesel engine? | 0.880885 | refused |
| Who won the 1994 World Cup? | 0.981905 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.835115 | refused |
| How do I write a for loop in Rust? | 0.858866 | refused |

```text
I don't have enough information about that.
```

**Criterion 4:** produced by `chunker.py::split_documents`, sampled in `tools/audit_chunks.py::audit`, `guide_corry_vale.md#5`:

```text
Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

The preamble `guide_accessibility.md#0` is the one sample without a section heading. The other sample labels are `guide_givens_mill.md#2`, `guide_kestrelford.md#4`, and `guide_pellew_sands.md#6`; all five full outputs are saved in `results/chunks-before.json`.

**Criterion 5:** generated by `generate.py::answer_from_chunks`, Q5 run 1:

```text
According to the documents, Kestrelford's pubs serve food only between 12 and 2 and between 6 and 8:30, and outside those windows "there is nowhere to eat at all" (which applies to Sunday evenings as well, though Sunday evening is noted as being particularly hard to find anywhere except Marchwood and Thornby Wells). 

Sources: `guide_kestrelford.md` and `guide_eating.md`
```

Its cited `guide_eating.md#1` actually contains the fact, retrieved by `store.py::search`:

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

Full answers and chunks for all 15 runs: [baseline report](results/run_2026-09-30_163337_before.md) and [structured evidence](results/evidence_2026-09-30_163317_before.json). The run made 15 real model calls with zero cache hits, using `cache=False`; repeated wording in some answers is not a cached replay.

### Setup and measurement controls

The existing `.venv` was activated. The first `python test.py` passed nine checks but could not resolve the API hostname inside the network sandbox. `pip install -r requirements.txt` found the dependencies already satisfied; outside the sandbox all ten checks passed, including the real `gemini-3.5-flash-lite` call. `app.py ask` returned the original tower-fee answer from the existing index (a development cache hit). The baseline evaluation separately bypassed that cache.

The index contains 94 chunks and matches the current Unit 1 chunker exactly. It was not rebuilt. Baseline settings: `city_guides`, `all-MiniLM-L6-v2`, `gemini-3.5-flash-lite`, default index, top-k 5, threshold 0.6. No corpus, question, gate, embedding, or generation setting was changed before this run. `run_eval.py` was extended only to record complete chunk text, call counts, cache status, and incremental JSON evidence; `tools/audit_chunks.py` measures criterion 4 without changing the system.

## Verdicts

| Criterion | Verdict | Decision against the original target |
|---|---|---|
| 1 | MET | All five questions have the required facts in the top five chunks in every run, exceeding 4/5. |
| 2 | MET | Every one of the 15 in-scope generated answers names a source; each run scores 5/5. |
| 3 | MET | All five out-of-scope questions are refused at threshold 0.6, exceeding 4/5. |
| 4 | MET | All 94 bodies preserve word boundaries and four of the original five samples start at a source section heading; the preamble stays in the denominator. |
| 5 | MET | Each run scores 5/5: the cited documents contain the stated core facts, including the regional Sunday warning in `guide_eating.md`. |

There is no criterion-level miss to explain away. No target was lowered and no original criterion was revised. These criteria are measurable with the scope and sample made explicit above, but they do not measure every unsupported inference in a generated answer. Criterion 2's scope and criterion 4's sample protocol should have been written explicitly in Unit 1; criterion 5 also leaves room for a correct core fact alongside an unsupported extra claim.

## Diagnoses

No original criterion was missed. The targets were easy on this small, structured corpus: the gate questions are from completely unrelated domains, four factual questions have single-sentence answers, and retrieval found the fifth question's information in one chunk. Next time I would tighten criterion 1 to **5/5 in every run**, including separately chosen questions requiring genuine synthesis across documents. That is a future proposal, not a replacement target for these runs.

**Evidence-supported limitation, generation stage:** Q5 run 1 says the pub windows "apply to Sunday evenings as well". `guide_kestrelford.md#3` gives general pub hours; `guide_eating.md#1` repeats those hours and warns that Sunday evening is hard outside Marchwood and Thornby Wells. Neither confirms that Kestrelford pubs serve on Sunday. The chunks contain the warning, so this uncertainty is present upstream and is lost when generation treats general hours as day-specific availability. This is an unsupported inference, not proof that the pubs are closed. Runs 2 and 3 repeat hours and the caveat but also do not explicitly say Sunday opening is unconfirmed. The mechanism is incomplete handling of the source's qualifications; the original prompt's general grounding rule did not prevent it in run 1.

**Correction to the Unit 1 rationale:** the original notes say Q5 cannot be answered from one document and needs two. Inspection shows `guide_eating.md#1` contains both Kestrelford's hours and the Sunday warning. The original text remains visible; this correction explains why retrieval scored 5/5 without changing the criterion.

**Retrieval-stage opportunity:** the Q5 top five include lodging (`guide_kestrelford.md#5`), sightseeing (`guide_kestrelford.md#4`), and Sunday lunch (`guide_eating.md#3`). Only the first two chunks directly resolve the evening question. The semantic search retrieves related town material even when the section does not answer the question. This noise is observed; a causal effect on answer quality is only a hypothesis. The factual answers and source attributions still passed.

There is no evidence of a loading, chunking, or embedding failure on these questions: all required facts are loaded, the index matches the chunker, and their containing chunks are retrieved.

## The Improvement

### Declared before implementation: primary improvement

I will add one rule to `generate.py::GROUNDING_INSTRUCTION`: general opening hours do not confirm service on a particular day, and the answer must explicitly state that uncertainty unless the provided text confirms the day. This targets Q5's unsupported Sunday inference while keeping retrieval, chunks, models, corpus, gate, and all original criteria unchanged.

I will compare `before` to `after` with all five questions run three times and all five gate questions measured once. Alongside the unchanged five criteria, I will report the narrower supplementary observation: how many of the three Q5 answers explicitly state that Sunday service is unconfirmed. Baseline: **0/3**, read from the saved outputs. This observation was declared after the baseline, so it is exploratory and not an original acceptance criterion.

### Stretch plan, declared before implementation

After the primary comparison, I will make exactly one further change: reduce `config.py::TOP_K` from 5 to 3. I will measure it against the completed primary `after` state, retaining the prompt improvement, with a full `after_stretch` evaluation. This tests whether a smaller context retains the required facts and factual citations while reducing retrieved noise and measured prompt tokens. I predict no acceptance-criterion gain because the baseline already passes. Any quality or token change will be reported as measured, including regressions. No gate tuning, hybrid search, chunking, or other feature will be bundled with this comparison.

The primary prompt change and stretch top-k change will be separate commits and separate full evaluations. Results are recorded below.

### Primary implementation and Run Log - After

The only system diff in this comparison is one additional rule in `generate.py::GROUNDING_INSTRUCTION`. Top-k remains 5 and threshold remains 0.6; the 94-chunk index, corpus, questions, and both models are unchanged. No new index was needed.

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | Every in-scope answer, 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk word boundaries and section starts | No mid-word boundaries; at least 4 of 5 section starts | 0 violations; 4/5 | 0 violations; 4/5 | 0 violations; 4/5 | MET |
| 5. Sources named contain the fact | At least 4 of 5 questions | 5/5 | 5/5 | 5/5 | MET |

Criteria 3 and 4 are each measured once and repeated in the columns for the same deterministic reasons as baseline. Manual per-question labels for retrieval, source naming, and factual citation are PASS in all three runs for every question; required facts and cited source documents match the baseline support table.

#### Actual primary after outputs

**Criterion 1:** `store.py::search`, `chunker.py::split_documents`, Q5 run 1, `guide_eating.md#1`:

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

**Criterion 2:** `generate.py::answer_from_chunks`, Q1 run 1:

```text
It costs £2 to climb the church tower in Kestrelford (Source: guide_kestrelford.md).
```

**Criterion 3:** `run_eval.py::check_out_of_scope` / `gate.py::check`, Mongolia question, best distance 0.8083643325580883, refused:

```text
I don't have enough information about that.
```

**Criterion 4:** `chunker.py::split_documents`, audited by `tools/audit_chunks.py::audit`, guide_corry_vale.md#5:

```text
Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

**Criterion 5:** `generate.py::answer_from_chunks`, Q5 run 1; the cited factual hours and Sunday caveat appear in the chunk above:

```text
Based on the provided documents, Kestrelford's pubs serve food between 12 and 2 and again between 6 and 8:30, but outside those windows there is nowhere to eat at all. However, Sunday evening availability is unconfirmed as Sunday evening is noted generally as the hardest meal to find anywhere except Marchwood and Thornby Wells. *(Source: guide_kestrelford.md and guide_eating.md)*
```

All 15 complete answers and retrieved chunks: [primary after report](results/run_2026-09-30_163802_after.md), [JSON evidence](results/evidence_2026-09-30_163744_after.json), and [chunk audit](results/chunks-after.json). The evaluation made 15 real model calls, zero cache hits.

**Did it help?** The five original criteria stayed MET with identical scores. The supplementary Sunday-uncertainty observation improved from **0/3 to 3/3**: every after answer explicitly states that Sunday availability is unconfirmed. This is a small, exploratory result on one question, not proof of improvement on unseen questions. All primary after retrieved chunks and distances match baseline, localizing the observed wording change to generation. Prompt tokens increased from **8,358 to 9,078** (+720, 8.6%) because of the added instruction; output tokens changed from 714 to 709.

The next comparison will execute the previously declared stretch change, top-k 5 to 3, with this prompt held fixed.

## What's Still Broken

Pending the measured comparisons.

## What I'd Do Differently

Pending final reflection.
