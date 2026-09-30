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


**Unit 2 assistance:** I used Codex to inspect the existing repository and commit history, scan the Obsidian vault for course and device context, and run the original questions with caching disabled. Codex extended the evaluation harness to save chunks and call counts, manually checked answers and factual citations, and identified both the unsupported Sunday inference and the new Monday-closure contradiction in the stretch outputs. It implemented the one grounding-prompt rule and the separate top-k change, ran all three full evaluations, drafted this write-up and the reflection, and made the milestone commits. No automated scorer was used. The measured token counts and answers come from actual calls; the diagnoses distinguish observed failures from hypotheses. These judgments and the proposed future criteria remain for my review.

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
| 5. Sources named contain the fact | At least 4 of 5 questions | 4/5 | 5/5 | 5/5 | MET |

The gate was measured once on the original five `OUT_OF_SCOPE` questions because retrieval and the fixed cutoff are deterministic. Criterion 4 was also measured once: all 94 chunk bodies were checked against their original document word boundaries, and the same five sample labels printed in Unit 1 were used, including the preamble. A section start means the existing title/section prefix corresponds to a source `##` heading, not that the output retains Markdown heading syntax. The deterministic values are repeated in the three columns.

Criterion 2 uses the five generated in-scope answers, as specified by its Unit 1 rationale ("All five"). Gate refusals are measured separately in criterion 3 and intentionally have no fabricated citation. The literal phrase "Every answer" is broader than that rationale; next time I would make this scope explicit.

No `scorer.py` exists. These are manual judgments of the saved answers and chunks, not fabricated automated pass labels. For criterion 1, Q1 requires the tower fee, Q2 the railway closure year, Q3 both pub service windows, Q4 the annual flood frequency, and Q5 the Kestrelford evening window plus the Sunday caveat and regional exceptions. For criterion 5, I checked factual assertions against the named document, not just whether a retrieved filename appeared. An unsupported extra assertion counts as a failure even when the requested core fact has the right source.

| Question | Retrieved fact, each run | Names source, runs 1/2/3 | Factual citation, runs 1/2/3 | Supporting retrieved chunk |
|---|---|---|---|---|
| Tower fee | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_kestrelford.md#4` |
| Railway closure | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_regional_transport.md#0` |
| Elder Ness pub hours | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_elder_ness.md#3` |
| Elder Ness floods | PASS/PASS/PASS | PASS/PASS/PASS | PASS/PASS/PASS | `guide_elder_ness.md#1` |
| Kestrelford Sunday evening | PASS/PASS/PASS | PASS/PASS/PASS | FAIL/PASS/PASS | `guide_eating.md#1` |

The last row passes retrieval because the required hours and caveat are present. Run 1 fails factual attribution because it adds that the windows apply to Sunday evenings, which neither cited document confirms. Runs 2 and 3 report the hours and caveat without that unsupported guarantee.

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
| 5 | MET | Runs score 4/5, 5/5, 5/5. Q5 run 1 adds an unsupported Sunday assertion, but every run still meets the original 4/5 target. |

There is no criterion-level miss to explain away. No target was lowered and no original criterion was revised. These criteria are measurable with the scope and sample made explicit above, but they do not measure every unsupported inference in a generated answer. Criterion 2's scope and criterion 4's sample protocol should have been written explicitly in Unit 1; criterion 5 should state explicitly how to score unsupported extra claims. Here I counted those as failures consistently rather than crediting only a correctly sourced core fact.

## Diagnoses

No original criterion was missed. The targets were easy on this small, structured corpus: the gate questions are from completely unrelated domains, four factual questions have single-sentence answers, and retrieval found the fifth question's information in one chunk. Next time I would tighten criterion 1 to **5/5 in every run**, including separately chosen questions requiring genuine synthesis across documents. That is a future proposal, not a replacement target for these runs.

**Evidence-supported limitation, generation stage:** Q5 run 1 says the pub windows "apply to Sunday evenings as well". `guide_kestrelford.md#3` gives general pub hours; `guide_eating.md#1` repeats those hours and warns that Sunday evening is hard outside Marchwood and Thornby Wells. Neither confirms that Kestrelford pubs serve on Sunday. The chunks contain the warning, so this uncertainty is present upstream and is lost when generation treats general hours as day-specific availability. This is an unsupported inference, not proof that the pubs are closed. Runs 2 and 3 repeat hours and the caveat but also do not explicitly say Sunday opening is unconfirmed. The mechanism is incomplete handling of the source's qualifications; the original prompt's general grounding rule did not prevent it in run 1.

**Correction to the Unit 1 rationale:** the original notes say Q5 cannot be answered from one document and needs two. Inspection shows `guide_eating.md#1` contains both Kestrelford's hours and the Sunday warning. The original text remains visible; this correction explains why retrieval scored 5/5 without changing the criterion.

**Retrieval-stage opportunity:** the Q5 top five include lodging (`guide_kestrelford.md#5`), sightseeing (`guide_kestrelford.md#4`), and Sunday lunch (`guide_eating.md#3`). Only the first two chunks directly resolve the evening question. The semantic search retrieves related town material even when the section does not answer the question. This noise is observed; a causal effect on answer quality is only a hypothesis. All criterion-level targets still passed, although Q5 run 1 failed source support for its extra Sunday assertion.

There is no evidence of a loading, chunking, or embedding failure on these questions: all required facts are loaded, the index matches the chunker, and their containing chunks are retrieved.

## The Improvement

### Declared before implementation: primary improvement

I will add one rule to `generate.py::GROUNDING_INSTRUCTION`: general opening hours do not confirm service on a particular day, and the answer must explicitly state that uncertainty unless the provided text confirms the day. This targets Q5's unsupported Sunday inference while keeping retrieval, chunks, models, corpus, gate, and all original criteria unchanged.

I will compare `before` to `after` with all five questions run three times and all five gate questions measured once. Alongside the unchanged five criteria, I will report the narrower supplementary observation: how many of the three Q5 answers explicitly state that Sunday service is unconfirmed. Baseline: **0/3**, read from the saved outputs. This observation was declared after the baseline, so it is exploratory and not an original acceptance criterion.

### Stretch plan, declared before implementation

After the primary comparison, I will make exactly one further change: reduce `config.py::TOP_K` from 5 to 3. I will measure it against the completed primary `after` state, retaining the prompt improvement, with a full `after_stretch` evaluation. This tests whether a smaller context retains the required facts and factual citations while reducing retrieved noise and measured prompt tokens. I predict no acceptance-criterion gain because the baseline already passes. Any quality or token change will be reported as measured, including regressions. No gate tuning, hybrid search, chunking, or other feature will be bundled with this comparison.

The primary prompt change and stretch top-k change are separate commits and separate full evaluations. Results are recorded below.

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

**Did it help?** The five original criteria stayed MET. Criterion 5 improved from 4/5, 5/5, 5/5 to 5/5 in all three runs; the other four criterion scores stayed identical. The supplementary Sunday-uncertainty observation improved from **0/3 to 3/3**: every after answer explicitly states that Sunday availability is unconfirmed. This is a small, exploratory result on one question, not proof of improvement on unseen questions. All primary after retrieved chunks and distances match baseline, localizing the observed wording change to generation. Prompt tokens increased from **8,358 to 9,078** (+720, 8.6%) because of the added instruction; output tokens changed from 714 to 709.

The next comparison executed the previously declared stretch change, top-k 5 to 3, with this prompt held fixed.

### Stretch implementation and Run Log - After Stretch

The stretch was declared in commit `338bc0a` before either improvement began. Its only system change relative to primary `after` is `config.py::TOP_K = 3` instead of 5. The improved grounding prompt is held fixed. The corpus, models, threshold, chunker, and existing index are unchanged; the third evaluation still runs the same five questions three times, plus the five deterministic gate questions once.

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | Every in-scope answer, 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk word boundaries and section starts | No mid-word boundaries; at least 4 of 5 section starts | 0 violations; 4/5 | 0 violations; 4/5 | 0 violations; 4/5 | MET |
| 5. Sources named contain the fact | At least 4 of 5 questions | 4/5 | 4/5 | 4/5 | MET |

The verdicts follow the same rule as before: the requested facts are retrieved in all runs, all answers cite a source, the gate refuses 5/5, and the unchanged chunk audit passes. Criterion 5 scores 4/5 in each run: the pub answer has the right source for its hours, but its extra Monday-uncertainty assertion contradicts that source, so it fails. The other four answers pass. The 4/5 original target is met in every run without ignoring the contradiction. This is the same treatment given to the unsupported extra Sunday assertion in baseline Q5 run 1.

Criteria 3 and 4 are measured once and repeated. Manual retrieval and source-naming labels are PASS/PASS/PASS for every question. Factual attribution is FAIL/FAIL/FAIL for Q3 and PASS/PASS/PASS for the other four. The retained supporting chunk labels match the baseline support table.

#### Actual stretch outputs

**Criterion 1:** `store.py::search`, `chunker.py::split_documents`, Q3 run 1, `guide_elder_ness.md#3`:

```text
Elder Ness — Eat and drink

One pub, serving food 12 to 2 and 6 to 8, closed Mondays. A shop that sells basics and closes at 5pm and all day Sunday. That is the complete list. Visitors staying more than a night bring food with them.
```

**Criterion 2:** `generate.py::answer_from_chunks`, Q1 run 1:

```text
It costs £2 to climb the church tower in Kestrelford (from guide_kestrelford.md).
```

**Criterion 3:** `run_eval.py::check_out_of_scope` / `gate.py::check`, Mongolia question, best distance 0.8083643325580883, refused:

```text
I don't have enough information about that.
```

**Criterion 4:** `chunker.py::split_documents`, `tools/audit_chunks.py::audit`, guide_corry_vale.md#5:

```text
Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

**Criterion 5:** `generate.py::answer_from_chunks`, Q5 run 1:

```text
According to `guide_eating.md`, Sunday evening is the hardest meal to find anywhere except Marchwood and Thornby Wells, and Kestrelford's pubs serve food only between 12 and 2 and between 6 and 8:30 (with that day's specific availability otherwise unconfirmed), outside of which there is nowhere to eat at all.
```

Matching factual source chunk from `store.py::search`, `guide_eating.md#1`:

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

**Observed regression, Q3 run 1**, `generate.py::answer_from_chunks`:

```text
The pub at Elder Ness serves food from 12 to 2 and 6 to 8, but its availability on Mondays is unconfirmed because it is closed on Mondays (guide_elder_ness.md).
```

Full stretch evidence: [report](results/run_2026-09-30_164030_after_stretch.md), [JSON](results/evidence_2026-09-30_164005_after_stretch.json), and [chunk audit](results/chunks-after-stretch.json). It made 15 real model calls, zero cache hits.

**Did the stretch help?** It helped context cost but made the pub answer worse. Prompt tokens fell **9,078 to 6,501**, a reduction of **2,577 (28.4%)**, with the prompt instruction held fixed. Retrieved context fell from five to three chunks per question (75 to 45 chunks across the 15 calls). The first four criterion scores stayed unchanged; criterion 5 fell from 5/5 to 4/5 in every run, still meeting its target. Q5 still explicitly flags Sunday uncertainty in **3/3** runs. However, contradictory Monday-uncertainty language appears in **3/3** Q3 answers, versus **0/3** in baseline and **0/3** in the primary after run. This narrower regression check was discovered after the stretch, so it is exploratory, not a precommitted criterion.

**Regression diagnosis, generation stage and mechanism:** all three stretch Q3 runs retrieve `guide_elder_ness.md#3`, whose full text explicitly says "closed Mondays". Thus the answer is present in the context and the gate passes at best distance 0.168684; loading, chunking, and retrieval do not explain the Monday contradiction. Generation applies uncertainty language to an explicit closure, even though the question does not name Monday. A plausible mechanism is overgeneralization of the new day-specific instruction under the shorter context. The changed context and these three outputs support an association; they do not prove why the model applied the rule incorrectly. The prompt requires confirmation of service but does not explicitly distinguish confirmed non-service from unknown availability. That is a hypothesis for a future isolated prompt experiment, not a confirmed cause.

### Measured comparison

| Measure | Before | Primary after | Stretch after |
|---|---|---|---|
| Criterion 1, runs 1/2/3 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 |
| Criterion 2, runs 1/2/3 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 |
| Criterion 3, deterministic refusals | 5/5 | 5/5 | 5/5 |
| Criterion 4, deterministic audit | 0 word splits; 4/5 section starts | 0 word splits; 4/5 section starts | 0 word splits; 4/5 section starts |
| Criterion 5, runs 1/2/3 | 4/5, 5/5, 5/5 | 5/5, 5/5, 5/5 | 4/5, 4/5, 4/5 |
| Q5 explicitly says Sunday unconfirmed (exploratory) | 0/3 | 3/3 | 3/3 |
| Q3 contradicts Monday closure (exploratory) | 0/3 | 0/3 | 3/3 |
| Prompt tokens, reported by service | 8,358 | 9,078 | 6,501 |
| Output tokens, reported by service | 714 | 709 | 687 |
| Model calls / cache hits | 15 / 0 | 15 / 0 | 15 / 0 |

The final measured system retains both sequential changes: the day-specific grounding rule and top-k 3. This records the unsuccessful quality aspect of the stretch transparently; no third fix or silent rollback is bundled into the reported comparison.

## What's Still Broken

None of the five original criteria remains MISSED, but that does not mean the system is fully correct. The stretch introduced contradictory Monday-availability wording in all three pub answers, despite retrieving the explicit closure. Next I would run one isolated prompt experiment that treats explicit closures as confirmed non-service and applies uncertainty only to genuinely unspecified days. I would hold top-k at 3 and rerun the full suite, including an explicit check that "closed Mondays" stays a closure. I stopped here to preserve the primary and stretch comparisons as separate single changes, rather than bundling a third fix into either result.

The original evaluation set also has limited coverage. I would add near-domain out-of-scope questions (for example, exact bookings or current opening status absent from these fictional guides) to challenge the gate, and genuinely separate-document questions to test synthesis. The five original out-of-scope questions are so far from travel that a 5/5 result does not establish a well-calibrated gate for realistic unknowns. Those additions are future work; this submission keeps the original ten questions unchanged.

The corpus does not name a specific Kestrelford pub or verify Sunday service. A retrieval or prompt change cannot manufacture that missing information. With corpus changes outside this unit's scope, an honest uncertain answer is the appropriate limit.

## What I'd Do Differently

I would primarily rewrite **criterion 5** next time: "In all three runs, at least 4 of 5 answers have every factual claim supported by the source cited for that claim, with no contradiction of an explicit closure or other qualifier." The original is underspecified about extra assertions. I ultimately scored them as failures: Q5 run 1 before, and all three Q3 stretch answers. I would specify clause-level evidence and a rule for unsupported extras before running the next experiment, so this judgment does not need a final review clarification. Even this stricter scoring allows one failed answer per run, so I would also consider requiring 5/5 once the basic pattern is fixed. This is a future criterion, not a changed target used to grade these results.

For **criterion 1**, I would require 5/5 retrieval coverage and choose at least two questions whose required evidence truly lives in different documents. I would inspect the corpus carefully enough to avoid calling Q5 multi-document when one opening-hours chunk contains both facts. For **criterion 2**, I would explicitly say "all five generated in-scope answers" and describe citation-free gate refusals separately. For **criterion 4**, I would record the five sample labels and define a title/section prefix as a section start before testing. These are clarity and coverage improvements for the next unit, not easier replacement targets.

### Submission checklist and repository continuity

- `criteria.md` is byte-for-byte unchanged from Unit 1; all original targets and rationale remain visible.
- `questions.py`, all corpus documents, chunker, loader, embedder, gate, and `RUNNING.md` are unchanged.
- `results/` contains complete baseline, primary after, and stretch after evidence, full answers, retrieved chunks and distances, gate decisions, and chunk audits. Each phase has 15 uncached generated answers and five deterministic out-of-scope measurements.
- The README includes all five criteria in each run table, actual outputs with producing file/function, verdict explanations, diagnoses and their limits, two separately measured changes, remaining work, reflection, and AI disclosure.
- Unit 2 has at least four new milestone commits on top of `5e9663f`; the history is not rewritten.
- GitHub confirms this is the existing `cstljuan` fork of CodePath's starter; the Unit 1 commit `5e9663f` is attributed to the GitHub account `cstljuan`. The same existing remote URL is the URL to use again: **https://github.com/cstljuan/ai201-project1-unofficial-guide-starter-v2026**. A Unit 1 course-portal submission receipt is not present in the repository or vault, so I cannot independently verify the URL entered in that form.
- The original checkout remains under `~/Projects/CodePath/AI201/ai201-project1-unofficial-guide-starter-v2026`. `~/Projects/CodePath/AI201/Unit-2/project` is a link to this same checkout, and `unit2/README.md` is a committed module entry point.
- Changes are committed locally for review. Nothing was pushed or submitted externally in this session, following the requested review boundary. Publishing these commits to the existing fork and submitting that URL are still external steps.

### Reproducing the measured states

Activate the existing environment before running commands. `ff2055b` records the baseline system and evidence harness; `1593749` records the primary prompt improvement at top-k 5; `7497b55` records the stretch at top-k 3. Check out the corresponding state in this same repository to reproduce a phase, then run `python run_eval.py --label before`, `python run_eval.py --label after`, or `python run_eval.py --label after_stretch`, respectively. Run `python tools/audit_chunks.py --label LABEL` for the matching deterministic chunk audit. New API answers may vary; the committed logs preserve what was actually measured.

`run_eval.py` does not automatically score these answers because no `scorer.py` exists. The manually reviewed per-question labels, original criterion aggregates, and supplementary failure observations are preserved in `results/manual-judgments.json`. The exploratory checks are explicitly distinguished from the Unit 1 acceptance criteria.

### Final scoring audit correction

The initial draft counted only support for each answer's requested core fact in criterion 5. The final review applies the unchanged original source-support criterion conservatively to extra factual assertions as well. Therefore baseline Q5 run 1 is FAIL for its unsupported Sunday inference, and stretch Q3 is FAIL in all three runs for contradicting the explicit Monday closure. Baseline criterion 5 is **4/5, 5/5, 5/5**; primary after is **5/5, 5/5, 5/5**; stretch is **4/5, 4/5, 4/5**. All three still meet the original target of at least 4/5 in every run. Raw outputs are unchanged. This correction is a new commit rather than rewritten milestone history.
