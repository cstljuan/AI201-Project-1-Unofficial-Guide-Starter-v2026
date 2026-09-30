# Run log — after_stretch

- Produced by: `run_eval.py::main`
- Retrieval: `store.py::search`, chunks from `chunker.py::split_documents`
- Corpus: `city_guides` (index variant `default`)
- top-k: 3 · relevance cutoff: 0.6
- Runs per question: 3, caching off
- When: 2026-09-30 16:40

This table is one row per QUESTION. The run log your README asks for is
one row per CRITERION, so aggregate these into it — criterion 1 is how many
of your questions had the answer in the retrieved chunks, and so on.

| Question | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| How much does it cost to climb the church tower in Kestrelford? |   |   |   |
| When did the railway line north of Brightwater close? |   |   |   |
| What times does the pub at Elder Ness serve food? |   |   |   |
| How often does the road to Elder Ness flood? |   |   |   |
| Where can I eat in Kestrelford on a Sunday evening? |   |   |   |

> The Run columns are blank because `scorer.py` doesn't exist yet.
> Judge each question yourself by reading the output below, or build
> the scorer first and re-run.

---

## The relevance gate on out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.6. Refused 5 of 5.

Retrieval is deterministic and the gate is a comparison against a
fixed number, so these do not vary between runs — one pass over the
list is the whole measurement.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.808 | refused |
| How do I change the oil in a diesel engine? | 0.881 | refused |
| Who won the 1994 World Cup? | 0.982 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.835 | refused |
| How do I write a for loop in Rust? | 0.859 | refused |

---

## Real output

This is what the system actually produced. Paste the relevant parts
into your README underneath the table — the rubric asks for real
output as text, not a description of it.

### How much does it cost to climb the church tower in Kestrelford? — run 1

- Best distance: 0.4059 (passed the gate)
- Sources retrieved: guide_kestrelford.md

```
It costs £2 to climb the church tower in Kestrelford (from guide_kestrelford.md).
```

### How much does it cost to climb the church tower in Kestrelford? — run 2

- Best distance: 0.4059 (passed the gate)
- Sources retrieved: guide_kestrelford.md

```
It costs £2 to climb the church tower in Kestrelford (Source: guide_kestrelford.md).
```

### How much does it cost to climb the church tower in Kestrelford? — run 3

- Best distance: 0.4059 (passed the gate)
- Sources retrieved: guide_kestrelford.md

```
It costs £2 to climb the church tower in Kestrelford (guide_kestrelford.md).
```

### When did the railway line north of Brightwater close? — run 1

- Best distance: 0.2578 (passed the gate)
- Sources retrieved: guide_kestrelford.md, guide_regional_transport.md, guide_walking.md

```
The railway line north of Brightwater closed in 1963. This is mentioned in `guide_regional_transport.md` and `guide_walking.md`.
```

### When did the railway line north of Brightwater close? — run 2

- Best distance: 0.2578 (passed the gate)
- Sources retrieved: guide_kestrelford.md, guide_regional_transport.md, guide_walking.md

```
The railway line north of Brightwater closed in 1963. 

Sources: `guide_regional_transport.md` and `guide_walking.md`
```

### When did the railway line north of Brightwater close? — run 3

- Best distance: 0.2578 (passed the gate)
- Sources retrieved: guide_kestrelford.md, guide_regional_transport.md, guide_walking.md

```
The railway line north of Brightwater closed in 1963. 

Sources: `guide_regional_transport.md` and `guide_walking.md`
```

### What times does the pub at Elder Ness serve food? — run 1

- Best distance: 0.1687 (passed the gate)
- Sources retrieved: guide_eating.md, guide_elder_ness.md

```
The pub at Elder Ness serves food from 12 to 2 and 6 to 8, but its availability on Mondays is unconfirmed because it is closed on Mondays (guide_elder_ness.md).
```

### What times does the pub at Elder Ness serve food? — run 2

- Best distance: 0.1687 (passed the gate)
- Sources retrieved: guide_eating.md, guide_elder_ness.md

```
The pub at Elder Ness serves food from 12 to 2 and 6 to 8, but it is closed on Mondays (guide_elder_ness.md). Therefore, availability on Mondays is unconfirmed by general hours alone.
```

### What times does the pub at Elder Ness serve food? — run 3

- Best distance: 0.1687 (passed the gate)
- Sources retrieved: guide_eating.md, guide_elder_ness.md

```
The pub at Elder Ness serves food from 12 to 2 and 6 to 8, but its availability on Mondays is unconfirmed because the documents state it is closed on Mondays (guide_elder_ness.md and guide_eating.md).
```

### How often does the road to Elder Ness flood? — run 1

- Best distance: 0.2641 (passed the gate)
- Sources retrieved: guide_elder_ness.md

```
The single road into Elder Ness floods at the highest spring tides roughly six times a year for about two hours either side of high water (guide_elder_ness.md).
```

### How often does the road to Elder Ness flood? — run 2

- Best distance: 0.2641 (passed the gate)
- Sources retrieved: guide_elder_ness.md

```
The single road into Elder Ness floods at the highest spring tides roughly six times a year for about two hours either side of high water (guide_elder_ness.md).
```

### How often does the road to Elder Ness flood? — run 3

- Best distance: 0.2641 (passed the gate)
- Sources retrieved: guide_elder_ness.md

```
The single road into Elder Ness floods at the highest spring tides roughly six times a year for about two hours either side of high water. 

Source: guide_elder_ness.md
```

### Where can I eat in Kestrelford on a Sunday evening? — run 1

- Best distance: 0.2678 (passed the gate)
- Sources retrieved: guide_eating.md, guide_kestrelford.md

```
According to `guide_eating.md`, Sunday evening is the hardest meal to find anywhere except Marchwood and Thornby Wells, and Kestrelford's pubs serve food only between 12 and 2 and between 6 and 8:30 (with that day's specific availability otherwise unconfirmed), outside of which there is nowhere to eat at all.
```

### Where can I eat in Kestrelford on a Sunday evening? — run 2

- Best distance: 0.2678 (passed the gate)
- Sources retrieved: guide_eating.md, guide_kestrelford.md

```
Based on the provided documents, Kestrelford's pubs serve food between 12 and 2 and again between 6 and 8:30 (guide_kestrelford.md and guide_eating.md). However, the documents state that Sunday evening is the hardest meal to find anywhere except Marchwood and Thornby Wells (guide_eating.md), and general opening hours do not confirm service on a particular day, leaving Sunday availability unconfirmed.
```

### Where can I eat in Kestrelford on a Sunday evening? — run 3

- Best distance: 0.2678 (passed the gate)
- Sources retrieved: guide_eating.md, guide_kestrelford.md

```
Based on the provided documents, Kestrelford's pubs serve food between 6 and 8:30, but availability for Sunday evening is unconfirmed as general hours do not confirm service on a particular day, and Sunday evening is generally noted as the hardest meal to find outside Marchwood and Thornby Wells. 

Source: `guide_eating.md` and `guide_kestrelford.md`.
```

## Retrieved chunks for every question/run

### How much does it cost to climb the church tower in Kestrelford? / run 1

Model calls: 1; cache=False

guide_kestrelford.md#4 | distance 0.405935 | chunker.py::split_documents

```text
Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

guide_kestrelford.md#0 | distance 0.511073 | chunker.py::split_documents

```text
Kestrelford

Kestrelford is a hill town of 12,000, an hour inland from Brightwater. It has been a market town since the 1200s and the street plan has not meaningfully changed since. This is charming on foot and difficult in a car.
```

guide_kestrelford.md#2 | distance 0.532155 | chunker.py::split_documents

```text
Kestrelford — Getting around

Everything is within a ten-minute walk of the market square. The town is built on a slope and the walk up from the lower car park is steeper than it looks on a map. There is no local bus service within the town itself.
```

### How much does it cost to climb the church tower in Kestrelford? / run 2

Model calls: 1; cache=False

guide_kestrelford.md#4 | distance 0.405935 | chunker.py::split_documents

```text
Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

guide_kestrelford.md#0 | distance 0.511073 | chunker.py::split_documents

```text
Kestrelford

Kestrelford is a hill town of 12,000, an hour inland from Brightwater. It has been a market town since the 1200s and the street plan has not meaningfully changed since. This is charming on foot and difficult in a car.
```

guide_kestrelford.md#2 | distance 0.532155 | chunker.py::split_documents

```text
Kestrelford — Getting around

Everything is within a ten-minute walk of the market square. The town is built on a slope and the walk up from the lower car park is steeper than it looks on a map. There is no local bus service within the town itself.
```

### How much does it cost to climb the church tower in Kestrelford? / run 3

Model calls: 1; cache=False

guide_kestrelford.md#4 | distance 0.405935 | chunker.py::split_documents

```text
Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

guide_kestrelford.md#0 | distance 0.511073 | chunker.py::split_documents

```text
Kestrelford

Kestrelford is a hill town of 12,000, an hour inland from Brightwater. It has been a market town since the 1200s and the street plan has not meaningfully changed since. This is charming on foot and difficult in a car.
```

guide_kestrelford.md#2 | distance 0.532155 | chunker.py::split_documents

```text
Kestrelford — Getting around

Everything is within a ten-minute walk of the market square. The town is built on a slope and the walk up from the lower car park is steeper than it looks on a map. There is no local bus service within the town itself.
```

### When did the railway line north of Brightwater close? / run 1

Model calls: 1; cache=False

guide_regional_transport.md#0 | distance 0.257755 | chunker.py::split_documents

```text
Getting around the region — The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

guide_walking.md#0 | distance 0.347890 | chunker.py::split_documents

```text
Walking in the region — Easy, on good surfaces

The **Brightwater river path** runs four miles upstream from the town to a weir,
on a made surface, flat throughout. It is the most-walked route in the region
and deservedly so. Continuing downstream from Givens Mill reaches Brightwater in
about three hours.

The **Kestrelford trackbed** follows the railway line closed in 1963 for six
miles to the next village. Easy gradient, good surface, and the best walking in
the region for the effort involved.

**Thornby Wells** has flat, formal gardens and level streets — the region's
most accessible town on foot.
```

guide_kestrelford.md#1 | distance 0.389477 | chunker.py::split_documents

```text
Kestrelford — Getting there

No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, every two hours on Saturdays, and not at all on Sundays. Driving takes 55 minutes and the last eight are on a single-track road with passing places.
```

### When did the railway line north of Brightwater close? / run 2

Model calls: 1; cache=False

guide_regional_transport.md#0 | distance 0.257755 | chunker.py::split_documents

```text
Getting around the region — The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

guide_walking.md#0 | distance 0.347890 | chunker.py::split_documents

```text
Walking in the region — Easy, on good surfaces

The **Brightwater river path** runs four miles upstream from the town to a weir,
on a made surface, flat throughout. It is the most-walked route in the region
and deservedly so. Continuing downstream from Givens Mill reaches Brightwater in
about three hours.

The **Kestrelford trackbed** follows the railway line closed in 1963 for six
miles to the next village. Easy gradient, good surface, and the best walking in
the region for the effort involved.

**Thornby Wells** has flat, formal gardens and level streets — the region's
most accessible town on foot.
```

guide_kestrelford.md#1 | distance 0.389477 | chunker.py::split_documents

```text
Kestrelford — Getting there

No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, every two hours on Saturdays, and not at all on Sundays. Driving takes 55 minutes and the last eight are on a single-track road with passing places.
```

### When did the railway line north of Brightwater close? / run 3

Model calls: 1; cache=False

guide_regional_transport.md#0 | distance 0.257755 | chunker.py::split_documents

```text
Getting around the region — The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

guide_walking.md#0 | distance 0.347890 | chunker.py::split_documents

```text
Walking in the region — Easy, on good surfaces

The **Brightwater river path** runs four miles upstream from the town to a weir,
on a made surface, flat throughout. It is the most-walked route in the region
and deservedly so. Continuing downstream from Givens Mill reaches Brightwater in
about three hours.

The **Kestrelford trackbed** follows the railway line closed in 1963 for six
miles to the next village. Easy gradient, good surface, and the best walking in
the region for the effort involved.

**Thornby Wells** has flat, formal gardens and level streets — the region's
most accessible town on foot.
```

guide_kestrelford.md#1 | distance 0.389477 | chunker.py::split_documents

```text
Kestrelford — Getting there

No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, every two hours on Saturdays, and not at all on Sundays. Driving takes 55 minutes and the last eight are on a single-track road with passing places.
```

### What times does the pub at Elder Ness serve food? / run 1

Model calls: 1; cache=False

guide_elder_ness.md#3 | distance 0.168684 | chunker.py::split_documents

```text
Elder Ness — Eat and drink

One pub, serving food 12 to 2 and 6 to 8, closed Mondays. A shop that sells basics and closes at 5pm and all day Sunday. That is the complete list. Visitors staying more than a night bring food with them.
```

guide_eating.md#1 | distance 0.312668 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_elder_ness.md#5 | distance 0.341548 | chunker.py::split_documents

```text
Elder Ness — Where to stay

The pub has four rooms and the observatory has dormitory accommodation for members and their guests. Both book up entirely for the migration seasons a year ahead. There is nothing else.
```

### What times does the pub at Elder Ness serve food? / run 2

Model calls: 1; cache=False

guide_elder_ness.md#3 | distance 0.168684 | chunker.py::split_documents

```text
Elder Ness — Eat and drink

One pub, serving food 12 to 2 and 6 to 8, closed Mondays. A shop that sells basics and closes at 5pm and all day Sunday. That is the complete list. Visitors staying more than a night bring food with them.
```

guide_eating.md#1 | distance 0.312668 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_elder_ness.md#5 | distance 0.341548 | chunker.py::split_documents

```text
Elder Ness — Where to stay

The pub has four rooms and the observatory has dormitory accommodation for members and their guests. Both book up entirely for the migration seasons a year ahead. There is nothing else.
```

### What times does the pub at Elder Ness serve food? / run 3

Model calls: 1; cache=False

guide_elder_ness.md#3 | distance 0.168684 | chunker.py::split_documents

```text
Elder Ness — Eat and drink

One pub, serving food 12 to 2 and 6 to 8, closed Mondays. A shop that sells basics and closes at 5pm and all day Sunday. That is the complete list. Visitors staying more than a night bring food with them.
```

guide_eating.md#1 | distance 0.312668 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_elder_ness.md#5 | distance 0.341548 | chunker.py::split_documents

```text
Elder Ness — Where to stay

The pub has four rooms and the observatory has dormitory accommodation for members and their guests. Both book up entirely for the migration seasons a year ahead. There is nothing else.
```

### How often does the road to Elder Ness flood? / run 1

Model calls: 1; cache=False

guide_elder_ness.md#1 | distance 0.264103 | chunker.py::split_documents

```text
Elder Ness — Getting there

A single road in, which floods at the highest spring tides roughly six times a year for about two hours either side of high water. Tide tables are posted at the turning and are worth reading. No public transport of any kind. Nearest station is Pellew Sands, 40 minutes by road.
```

guide_elder_ness.md#6 | distance 0.376852 | chunker.py::split_documents

```text
Elder Ness — When to go

April to May and September to October for birds, which is what most visitors come for. Midsummer is pleasant and quiet. Winter is severe, the road floods more often, and the pub reduces to weekends only.
```

guide_elder_ness.md#0 | distance 0.416943 | chunker.py::split_documents

```text
Elder Ness

Elder Ness is a headland with a village of 300 on it, a lighthouse, a bird observatory, and very little else. People come for one of three reasons — birds, walking, or a deliberate absence of things to do.
```

### How often does the road to Elder Ness flood? / run 2

Model calls: 1; cache=False

guide_elder_ness.md#1 | distance 0.264103 | chunker.py::split_documents

```text
Elder Ness — Getting there

A single road in, which floods at the highest spring tides roughly six times a year for about two hours either side of high water. Tide tables are posted at the turning and are worth reading. No public transport of any kind. Nearest station is Pellew Sands, 40 minutes by road.
```

guide_elder_ness.md#6 | distance 0.376852 | chunker.py::split_documents

```text
Elder Ness — When to go

April to May and September to October for birds, which is what most visitors come for. Midsummer is pleasant and quiet. Winter is severe, the road floods more often, and the pub reduces to weekends only.
```

guide_elder_ness.md#0 | distance 0.416943 | chunker.py::split_documents

```text
Elder Ness

Elder Ness is a headland with a village of 300 on it, a lighthouse, a bird observatory, and very little else. People come for one of three reasons — birds, walking, or a deliberate absence of things to do.
```

### How often does the road to Elder Ness flood? / run 3

Model calls: 1; cache=False

guide_elder_ness.md#1 | distance 0.264103 | chunker.py::split_documents

```text
Elder Ness — Getting there

A single road in, which floods at the highest spring tides roughly six times a year for about two hours either side of high water. Tide tables are posted at the turning and are worth reading. No public transport of any kind. Nearest station is Pellew Sands, 40 minutes by road.
```

guide_elder_ness.md#6 | distance 0.376852 | chunker.py::split_documents

```text
Elder Ness — When to go

April to May and September to October for birds, which is what most visitors come for. Midsummer is pleasant and quiet. Winter is severe, the road floods more often, and the pub reduces to weekends only.
```

guide_elder_ness.md#0 | distance 0.416943 | chunker.py::split_documents

```text
Elder Ness

Elder Ness is a headland with a village of 300 on it, a lighthouse, a bird observatory, and very little else. People come for one of three reasons — birds, walking, or a deliberate absence of things to do.
```

### Where can I eat in Kestrelford on a Sunday evening? / run 1

Model calls: 1; cache=False

guide_kestrelford.md#3 | distance 0.267824 | chunker.py::split_documents

```text
Kestrelford — Eat and drink

Four pubs, two cafés, and a bakery that sells out by 11am. The pubs serve food between 12 and 2 and again between 6 and 8:30, and outside those windows there is nowhere to eat at all. The bakery is the reason most people come back.
```

guide_eating.md#1 | distance 0.326771 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_kestrelford.md#5 | distance 0.365223 | chunker.py::split_documents

```text
Kestrelford — Where to stay

Two inns on the square and a handful of rooms above the pubs. Booking ahead matters between May and September and not at all otherwise. There is no accommodation of any kind within four miles of the town in either direction.
```

### Where can I eat in Kestrelford on a Sunday evening? / run 2

Model calls: 1; cache=False

guide_kestrelford.md#3 | distance 0.267824 | chunker.py::split_documents

```text
Kestrelford — Eat and drink

Four pubs, two cafés, and a bakery that sells out by 11am. The pubs serve food between 12 and 2 and again between 6 and 8:30, and outside those windows there is nowhere to eat at all. The bakery is the reason most people come back.
```

guide_eating.md#1 | distance 0.326771 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_kestrelford.md#5 | distance 0.365223 | chunker.py::split_documents

```text
Kestrelford — Where to stay

Two inns on the square and a handful of rooms above the pubs. Booking ahead matters between May and September and not at all otherwise. There is no accommodation of any kind within four miles of the town in either direction.
```

### Where can I eat in Kestrelford on a Sunday evening? / run 3

Model calls: 1; cache=False

guide_kestrelford.md#3 | distance 0.267824 | chunker.py::split_documents

```text
Kestrelford — Eat and drink

Four pubs, two cafés, and a bakery that sells out by 11am. The pubs serve food between 12 and 2 and again between 6 and 8:30, and outside those windows there is nowhere to eat at all. The bakery is the reason most people come back.
```

guide_eating.md#1 | distance 0.326771 | chunker.py::split_documents

```text
Eating across the region — Opening hours

This catches visitors out more than anything else. Outside Marchwood, kitchens
across the region stop serving at 9pm and often earlier. Kestrelford's pubs
serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those
windows. Elder Ness has one pub, closed Mondays.

Sunday evening is the hardest meal to find anywhere except Marchwood and
Thornby Wells.
```

guide_kestrelford.md#5 | distance 0.365223 | chunker.py::split_documents

```text
Kestrelford — Where to stay

Two inns on the square and a handful of rooms above the pubs. Booking ahead matters between May and September and not at all otherwise. There is no accommodation of any kind within four miles of the town in either direction.
```

## Cache audit

15 model calls this session, 7188 tokens (6501 in, 687 out)
