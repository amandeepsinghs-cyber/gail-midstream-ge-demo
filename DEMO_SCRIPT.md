# One Morning at GAIL — Stage Script (V3)

**Audience:** ~300 GAIL employees across verticals · **Runtime:** ~8 minutes · **App:** Gemini Enterprise → GAIL Pipeline Agent

**The one idea to land:** *Any data → any model → any report, in one conversation. We show it on gas. You swap in your own work.*

> [!NOTE]
> Nominations, SCADA history and LNG prices are **illustrative demo data**. The SARIMAX model and the landed-cost formulas are real and run live.

---

## Opening (30 seconds, no screen yet)

> "It's 6 AM at the National Gas Management Centre. Overnight, customers revised tomorrow's nominations.
> Three questions land on one desk before the 9 AM call: **Can we supply it? What's the cheapest gas? Will the pipeline hold?**
> Today that is four people, five systems and a morning of spreadsheets. Watch one conversation do it."

---

## Beat 1 — The Problem (data access)

**Prompt:**
> Show me today's grid flows and tomorrow's customer nominations.

**What appears:** Grid-flow card plus the nomination alert.
- Fertilizer is up +3.0 MMSCMD and CGD is up +1.01 MMSCMD.
- That is a **4.0 MMSCMD shortfall from 08:00**.

**Say:**
> "It pulled SCADA, GIS and commercial nominations from our data lake and reconciled them. It found a gap nobody asked it to look for."

**Swap this for yours:** *"Finance: this is your receivables plus the bank feed. HR: rosters against leave. Same move."*

---

## Beat 2 — The Decision (deterministic model #1)

**Prompt:**
> What's the cheapest way to cover that shortfall?

**What appears:** Delivered-cost bar chart at Dahej for three options.

| Option | Delivered cost | Verdict |
|---|---|---|
| Qatar time-swap | **$11.83/MMBtu** | Recommended |
| Spot cargo (JKM) | $14.45 | Dearer |
| US Henry Hub re-route | $10.02 | Too late: arrives in 34 days, but we only have 7 days of cover |

- **Saving vs spot: ₹70.3 Cr.**

**Say:**
> "Notice it didn't just pick the cheapest number. Henry Hub is cheapest on paper but arrives after we run out. That is a constraint, and fixed formulas enforce it, not guesswork."

**Swap this for yours:** *"Procurement: vendor bids against delivery dates. Projects: contractor quotes against schedule."*

---

## Beat 3 — The Proof (deterministic model #2)

**Prompt:**
> Can the grid carry it? Forecast Chhainsa for 24 hours.

**What appears:** A five-step model workflow, then one chart read left to right:
- **Navy line (last 48h, actual):** the daily rhythm. Line-pack packs overnight and drafts through the day (~2.8 kg/cm² swing).
- **"Now" marker at 06:00**, where the forecast begins.
- **Red dashed line with cones (without action):** crosses the 76 kg/cm² contract floor at **19:00 (T+14h)**.
- **Green dashed line with cones (with the LNG swap):** bottoms at **79.53 kg/cm²**. Even the 95% band stays above the floor.
- **Validation:** trained on 48h, predicted the last 24h with **0.33% error**.
- **Setpoint:** Vijaipur +3.8%.

**Say (walk the chart left to right):**
> "On the left is what actually happened: the grid breathes every day. The agent loaded that history, learned the pattern, and proved it by predicting yesterday with a third of a percent error.
> Now look right. The shaded cones are its confidence, and they widen because the future is uncertain. Red is tonight if we do nothing: a breach at 7 PM. Green is tonight with the swap: safe, even at the edge of the cone.
> A forecast tells you what will happen. This tells you what will happen **if you act**."

**Swap this for yours:** *"Any forecast you run in Excel today: demand, cash flow, manpower, maintenance. Plus the 'what if we act' version."*

---

## Beat 4 — The Action (report + system of record)

**Prompt:**
> Brief management and raise the SAP order.

**What appears:** A "Decision on one page" card, a link to the full HTML briefing, and a staged SAP work order ID.

**Say:**
> "One page for the MD with the decision, the money and the risk. Every number traces back to the charts you just saw. The SAP order is staged for human approval, not auto-posted."

**Swap this for yours:** *"Your monthly MIS, your board note, your audit pack."*

---

## Close (20 seconds)

> "Four questions. Data, two models, a report and an ERP entry. One conversation.
> Nothing here was gas-specific except the data. **What is the 6 AM question on your desk?**"

---

## Backup prompts (if something stalls)

| Situation | Prompt |
|---|---|
| Card didn't render | "Show that as a chart." |
| Audience asks "how does the model work?" | "Explain the SARIMAX model and its fit quality." |
| Report link slow | "Summarise the decision in three bullets." |
| Fresh start needed | Open a **new chat** and restart from Beat 1 |

## Pre-flight checklist (T-15 min)
- [ ] Open a new chat in the GE app and run Beat 1 once to warm the engine (first SARIMAX fit takes about 4s).
- [ ] Confirm the GAIL logo shows on the agent tile.
- [ ] Open the report link once in a browser signed in to the demo account.
- [ ] Close the warm-up chat and open a fresh one for the stage.
