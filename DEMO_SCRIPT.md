# The Winter Call: Stage Script (V4, extended)

**Audience:** ~300 GAIL employees, including traders · **Runtime:** ~12 minutes · **App:** Gemini Enterprise → GAIL Gas Supply Decision Agent

**The thesis:** *A critical decision needs data from many systems. Gemini Enterprise gathers the **data** (GAIL's systems and the outside world), **analyses** it, helps the experts **decide**, and **acts** on it.*

**Closing line:** *"Bloomberg knows the market. SAP knows GAIL. Only Gemini Enterprise puts them in one decision."*

> [!IMPORTANT]
> **Market prices are LIVE** (Yahoo Finance), and news is live (Google Search). The numbers below are from the 24 Sep rehearsal and **will be different on the day**. Read the numbers off the screen, not this page.
> GAIL's contract book, supply plan, Dahej inventory, SAP orders and budget, and policy are **SAMPLE data** stored in the data lake (`gs://gail-midstream-ge-demo-datalake/raw/gail_internal/`).

Every card tags each number with where it came from: 🏢 = GAIL data, 🌐 = outside data. **Point at the tags.** They carry the Gemini Enterprise story.

| Stage | Questions |
|---|---|
| **Data** | Q1 the problem · Q2 our own position · Q3 the market |
| **Analysis** | Q4 context · Q5 outlook · Q6 Monte Carlo |
| **Decision** | Q6 recommendation |
| **Action** | Q7 |

---

## Opening (45 seconds, your slide)

> "Qatar supplies a large share of India's LNG. This year Ras Laffan is under force majeure. Europe and Asia are competing for every spare cargo, TTF is near €74 and Brent is around $100.
> GAIL has a winter to get through, and the desk has one critical call to make: **do we lock in replacement cargoes now, or wait for prices to fall?**
> Get it wrong and it costs hundreds of crores. Watch how Gemini Enterprise helps our experts make that call."

---

## Q1 · Data: the problem (GAIL data + news)

**Prompt:**
> What is the impact of the Qatar force majeure on our winter gas supply?

**What appears:** Winter supply-gap card.
- **6 cargoes (~19 TBtu) short, Dec–Feb.**
- Fertilizer and city gas are protected.
- **Every $1/MMBtu move is worth ₹184 Cr.**

**Say:**
> "It read our contract book and winter plan from the data lake 🏢, and checked today's news 🌐. We are six cargoes short this winter."

---

## Q2 · Data: our own position (the internal-data moment)

**Prompt:**
> Check our own position: inventory, customer commitments.

**What appears:** "Our own position: inventory, customers, SAP" card, with a deadline chart.
- ⏱️ **Deadline: the December cargoes must be contracted by 17 Oct, 23 days from today** (45-day lead time).
- 🛢️ **Dahej tanks:** 6.1 TBtu, only 3.6 usable (7 days of cover). **Not enough to absorb a missed month** (~7 TBtu).
- 👥 **Customers:** fertilizer and city gas are must-supply (60 of 96 MMSCMD). A missed cargo means a cut to other customers and about ₹61 Cr in compensation.
- 📄 **SAP:** no purchase order covers the gap; the Qatar order is **blocked (force majeure)**.
- 💰 **SAP budget:** replacement budget ₹4,053 Cr, nothing committed yet.
- ✍️ **Approver:** Director (Marketing), under the delegation of authority.

**Say (the key moment):**
> "Now our own systems: tanks, customers, open orders, budget, sign-off rules. No market terminal has any of this.
> And there's a **deadline**: we can only wait 23 days for December, and our tanks can't absorb a missed cargo."

---

## Q3 · Data: the market vs our contracts and budget

**Prompt:**
> What is gas costing today, and what does that mean for our contracts and our budget?

**What appears:** Live-market card.
- Henry Hub ~$3.1, TTF ~€74 (≈$25/MMBtu), Brent ~$100, plus the winter futures.
- **Our US contract cargo lands at ~$10.9** vs **~$24.9** to replace it at spot.
- Replacing Qatar costs about **₹2,060 Cr extra** this winter.
- 💰 Locking in all 6 cargoes at today's futures costs **~₹4,593 Cr, ₹540 Cr over the SAP budget**.

**Say:**
> "These prices were fetched seconds ago 🌐 and applied to **our** contracts and **our** SAP budget 🏢. Locking in today costs more than we budgeted."

---

## Q4 · Analysis: context

**Prompt:**
> How have gas prices moved over the last 5 years, and what drove them?

**What appears:** 5-year weekly chart of TTF, Henry Hub and Brent: the 2022 spike, today's spike, and TTF volatility of ~90% a year.

**Say:**
> "This market swings hard. That is what makes waiting risky."

---

## Q5 · Analysis: the experts

**Prompt:**
> What do the experts expect?

**What appears:** Dated, sourced forecasts from BofA, Goldman, EIA, Fitch and Enverus. The 2027 consensus is well below today, but the spread is wide.

**Say:**
> "Experts expect prices to fall, but they disagree by how much. So waiting is a bet. So let's test that bet properly."

---

## Q6 · Analysis → Decision (Monte Carlo)

**Prompt:**
> Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?

**What appears:** The answer opens with the method ("I simulated 10,000 winter price paths…"), then a strategy card with a fan chart and three strategies (lock all / lock half / wait until each deadline).
- 10,000 simulated price paths, from live futures, 5-year volatility and the analyst consensus. Waiting is priced at each month's contracting deadline.
- **Recommendation: lock in all 6 cargoes now.**
  - Waiting is cheaper in about **60%** of simulated futures, but saves only about **₹118 Cr** on average.
  - In the worst 5%, waiting costs about **₹2,300 Cr more**, which breaks GAIL's **₹800 Cr risk limit** 🏢.
- The card lists the internal checks: tanks, deadline, budget, approver.

**Say:**
> "This isn't gut feel. It simulated 10,000 possible winters and tested every option against our risk limit and deadlines.
> Waiting might save a little. But the downside breaks our risk limit, our tanks can't absorb a missed cargo, and the clock is already running.
> The market data and our own data point the same way. It doesn't replace the expert; it gives the Director the full picture in minutes."

---

## Q7 · Action

**Prompt:**
> Prepare the approval and stage it in SAP.

**What appears:** Approval card: the **approver** (set by the delegation of authority), a **link to the approval memo** (HTML with charts and a "checked against GAIL's position" section, in GCS), and an **SAP purchase requisition AWAITING APPROVAL**.

**Say:**
> "It picked the right approver from our own rules, wrote the memo with every number traced, and staged the order in SAP. **Nothing moves until a human approves.**"

---

## Close (20 seconds)

> "Seven questions, one conversation. Data from our contracts, tanks, customers, SAP and the market, **gathered, analysed, decided and actioned**.
> Bloomberg knows the market. SAP knows GAIL. **Only Gemini Enterprise puts them in one decision.**"

---

## Talk-track for tricky moments

| If… | Say |
|---|---|
| News says Qatar may restart in November | "Maybe. But our December deadline is in 23 days and our tanks can't cover a missed cargo. We can't plan a winter on maybe." |
| "Is the recommendation always 'lock in'?" | "No. It depends on today's prices, our risk limit and our deadlines. Change the limit or the budget and it can say 'lock in half'." |
| "Is this real GAIL data?" | "The market data is live. The contracts, inventory, SAP orders and policy are sample data in a data lake. Plug in the real systems and the same flow runs." |
| "Why not just use ChatGPT / Bloomberg?" | Ask the agent: **"Why do we need Gemini Enterprise for this?"** |
| "Will it trade on its own?" | "No. It stages the SAP request; a human approves." |

## Optional Q8 (only if asked about the pipeline)

> Can the pipeline take the volumes?

This shows the V3 SARIMAX line-pack chart. It uses an **illustrative +4.0 MMSCMD** swap, not the 5.7 MMSCMD winter gap. Call it "an example of the pipeline check".

## Backup prompts (if something stalls)

| Situation | Prompt |
|---|---|
| Card didn't render | "Show that as a chart." |
| Answer too long | "Summarise that in three bullets." |
| Memo link slow | "Summarise the approval in three bullets." |
| Fresh start needed | Open a **new chat** and restart from Q1 |

## Pre-flight checklist (T-15 min)
- [ ] Open a new chat and run Q1–Q2 once to warm the engine and the price cache.
- [ ] Note today's headline numbers: TTF, gap cost, **days to the December deadline**, and the recommendation.
- [ ] Check what today's Qatar news says, and have the talk-track line ready.
- [ ] Open the memo link once in a browser signed in to the demo account.
- [ ] Close the warm-up chat and open a fresh one for the stage.
