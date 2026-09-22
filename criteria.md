# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** Four of my five questions are answered by a single
sentence inside one document, so I expect retrieval to find them. The fifth
("Where can I eat in Kestrelford on a Sunday evening?") cannot be answered from
one document at all — `guide_kestrelford.md` gives the pub serving windows and
`guide_eating.md` separately says Sunday evening is hard to find anywhere
except Marchwood and Thornby Wells. I set the target at 4 rather than 5 because
I expect that one to miss, and I would rather name it now than explain it
afterwards.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** All five, because naming a source is mechanical rather
than a judgement call. Every chunk enters the prompt with a `[from filename]`
header (`generate.py::build_prompt`) and the system instruction tells the model
to name the file. The relevance gate also means the model never sees a thin
context it might hedge on. For this to fail the model would have to ignore a
direct instruction while the filename sits in front of it, so anything less
than 5 of 5 would point at a real defect rather than bad luck.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** The five out-of-corpus questions are about diesel
engines, ibuprofen, Rust, the 1994 World Cup and the capital of Mongolia — a
corpus of regional travel guides shares no vocabulary with any of them, so I
expect their distances to sit clearly above my in-corpus questions. I set 4 of
5 rather than 5 of 5 because the cutoff is a single number separating two
groups I have not measured yet, and one borderline case would not mean the gate
is broken.

<!-- TODO (Milestone 4): replace the expectation above with the ten distances I
     actually measured, and say whether the two groups had a clean gap. -->

---

## 4. Something about your chunks

No chunk begins or ends in the middle of a word, and at least 4 of my 5 sampled
chunks start at a section heading.

**Why this target:** The starter's fixed-size chunker cuts on a character count
and ignores the text completely. Sampling three chunks showed two of them
broken mid-word — `guide_elder_ness.md#1` opens with "re is one car park" and
`guide_marchwood.md#3` opens with "d in smaller places", because the preceding
chunk took the first characters of each word. Every document in `city_guides`
is divided by `##` headings, so a chunk that starts at a heading is a chunk
that starts at the beginning of a thought. Mid-word breaks are the clearest
countable symptom of splitting on length instead of structure, and they are
currently failing, so this is a target I can actually miss.



---

## 5. Sources named are the sources the fact came from

For at least 4 of my 5 questions, the document named in the answer is a
document that actually contains the fact — not merely a document that was
retrieved.

**Why this target:** Criterion 2 only asks that *a* source is named, which a
system can satisfy while citing the wrong file. Five of my fourteen documents
cut across all the towns (`guide_eating.md`, `guide_walking.md`,
`guide_regional_transport.md`, `guide_seasons.md`, `guide_accessibility.md`),
and several facts appear in both a town guide and a cross-cutting one — the
1963 railway closure is in `guide_kestrelford.md` and
`guide_regional_transport.md` both. With five chunks retrieved per question,
the model can easily attach the right answer to the wrong filename. I set 4 of
5 rather than 5 of 5 because my Sunday-evening question legitimately draws on
two documents, and I am not going to call it wrong for naming either one.



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
