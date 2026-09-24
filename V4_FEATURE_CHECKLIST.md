# GAIL V4 — Feature Checklist

**Rule:** every feature must help answer a business question on stage. If it doesn't, it's out.

**Framing:** we introduce a real GAIL business problem, then show Gemini Enterprise acting as a
**decision intelligence engine**. It helps GAIL's experts make the critical call and shows the value in ₹.

**The Gemini Enterprise test (every question must pass it):** *Could Bloomberg answer this alone? ChatGPT? SAP?*
If the answer needs **GAIL's own data + outside data + action back into GAIL's systems**, it's a Gemini Enterprise answer.
Closing line: *"Bloomberg knows the market. SAP knows GAIL. Only Gemini Enterprise puts them in one decision."*

Status: ✅ done & tested · 🟡 built, not fully tested / needs change · ⬜ not started · 👤 needs a human

---

## 1. The business problem and questions

**Business problem (confirmed):** *Qatar LNG is under force majeure. GAIL has a winter supply gap.
Do we lock in replacement cargoes now, or wait?*

| # | Business question (asked on stage) | 🏢 GAIL data (sample) | 🌐 Outside data | Answer the agent must give |
|---|---|---|---|---|
| Q0 | *Where does GAIL make money, and what's the risk?* (opening slide) | — | — | Presenter slide; thin margin that moves with price 👤 |
| Q1 Data | *What is the impact of the Qatar force majeure on our winter gas supply?* | Contract book, cargo schedule, customer nominations | Live news: Qatar outage (Google Search) | Winter gap in cargoes and TBtu, which customers are exposed, and ₹ exposure per $1 move |
| Q2 Data 🆕 | *Check our own position: inventory, customer commitments.* | Dahej inventory, must-supply customers + compensation, SAP open POs + budget, lead time, delegation of authority | — | Contracting deadline per month, whether tanks can absorb a missed month, what SAP already covers, budget, approver |
| Q3 Data | *What is gas costing today, and what does that mean for our contracts and our budget?* | Our contract formulas, SAP budget | Live Henry Hub, TTF, Brent, ₹/$, winter futures | Live prices in $/MMBtu, US cargo landed cost vs replacement spot, lock-in cost vs SAP budget |
| Q4 Analysis | *How have gas prices moved over the last 5 years, and what drove them?* | — | 5-year weekly history | The 2022 spike, today's spike, the spread, the volatility |
| Q5 Analysis | *What do the experts expect?* | — | Dated, sourced analyst forecasts | Forecasts, consensus, and how far apart the analysts are |
| Q6 Analysis → Decision | *Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?* | Everything in Q1–Q3, board risk limit | Futures, history-based volatility, analyst consensus | Method in one line, 3 strategies, expected ₹ cost, worst case (P95), probability, recommendation within the risk limit, checked against GAIL's position |
| Q7 Action | *Prepare the approval and stage it in SAP.* | SAP (purchase request), delegation of authority | — | Approver picked by value, approval memo, SAP purchase request **pending human approval** |
| Q8 (optional) | *Can the pipeline take the volumes?* | SCADA (illustrative) | — | Existing SARIMAX pipeline chart from V3 |

---

## 2. Feature list

### A. Outside data (answers Q2–Q4)
- [x] **A1 Yahoo Finance integration.** Live HH (NG=F), TTF (TTF=F), Brent (BZ=F), USD/INR, EUR/USD — ✅ tested live 24 Sep
- [x] **A2 Unit conversion.** TTF €/MWh → $/MMBtu, Brent → oil-parity $/MMBtu — ✅
- [ ] **A3 Stage safety net.** Yahoo → last saved copy in GCS → bundled snapshot; the card labels the source — 🟡 built; GCS path not yet tested
- [x] **A4 5-year weekly history.** 257 weeks, volatility and correlation — ✅
- [x] **A5 Analyst outlook table.** Verified rows only, with date, period, unit, URL; consensus = median of 2027 forecasts — ✅ 8 verified points; consensus = median of 2027 forecasts
- [ ] **A6 Human check of analyst URLs** before stage — 👤
- [x] **A7 Winter futures.** TTF Dec-26/Jan-27 settlements, HH Dec/Jan/Feb, Brent Dec/Jan — ✅ live settlements (TTF Feb-27 not on free feed → Jan carried, labelled)

### G. GAIL internal data + the Gemini Enterprise differentiators (answers Q1, Q2, Q5, Q6)
- [x] **G1 Sample GAIL data set.** Contract book, winter cargo schedule, Dahej inventory, customer nominations, budget and risk policy; stored in the data lake; labelled *"sample data; your data plugs in here"* — ✅ contract book, supply plan, policy (uploaded to gs://gail-midstream-ge-demo-datalake/raw/gail_internal/ on 24 Sep; loader verified reading from GCS)
- [x] **G2 Live news grounding.** Google Search sub-agent finds the Qatar outage news itself — ✅ tested live: agent finds Qatar/Ras Laffan news itself
- [x] **G3 "Sources" line on every card.** 🏢 GAIL data vs 🌐 market data — ✅
- [x] **G5 Internal position step (Q2, data first).** Dahej inventory, customer commitments, SAP open orders and budget (`sap_open_position.json`), contracting deadlines, delegation of authority — ✅ added 24 Sep after presenter review
- [x] **G6 Decision deadline is a hard rule.** Waiting is priced at each month's contracting deadline (delivery month − 45 days); past-deadline months are forced to lock — ✅ tested
- [x] **G7 Approver by delegation of authority.** SAP PR and memo routed by value (ED LNG ≤ ₹500 Cr, Director Marketing ≤ ₹5,000 Cr, Board above) — ✅ tested
- [ ] **G4 (optional) Permission moment.** *"Contract prices visible to Marketing only"* — ⬜ optional

### B. Analytics — the decision engine (answers Q1, Q5)
- [x] **B1 Gap engine.** Demand − (domestic + contracted arrivals + inventory) → gap in cargoes; priority-customer check — ✅ 6 cargoes Dec–Feb; priority customers protected
- [x] **B2 Deterministic pricing.** Lock-in cost from live futures; our US cargo landed cost vs spot — ✅ US contract $10.9 vs spot $24.9; Qatar outage ≈ ₹2,060 Cr
- [x] **B3 Monte Carlo.** 10,000 seeded paths, 5-year volatility, centred on analyst consensus → 3 strategies (lock 100% / hedge 50% / wait), expected ₹, P95, probability — ✅ seeded, reproducible (tested)
- [x] **B4 Recommendation rule (GAIL policy).** Cheapest expected strategy whose worst case stays inside the board risk limit — ✅ plus minimum cargoes to lock
- [x] **B5 Analyst sanity check.** Analyst forecasts plotted on the simulated fan — ✅ 4 of 4 inside the simulated range

### C. Agent tools + Gemini Enterprise cards (one per question)
- [x] **C1** Q1 card: supply vs demand by month, gap, exposed customers, news headline — ✅
- [x] **C2** Q2 card: live prices + our contract costs vs spot — ✅
- [x] **C3** Q3 card: 5-year TTF vs HH chart — ✅
- [x] **C4** Q4 card: analyst forecasts + consensus — ✅
- [x] **C5** Q5 card: 3 strategies, fan chart, recommendation — ✅
- [x] **C6** Q6 card: memo link + SAP request "Pending approval" — ✅
- [x] **C7** Keep V3 SARIMAX card as optional Q7 — exists (illustrative +4.0 MMSCMD swap, not the V4 5.7 gap)

### D. Action (answers Q6)
- [x] **D1** Approval memo (HTML with charts) published to GCS, clickable link — ✅ published to GCS in rehearsal
- [x] **D2** SAP purchase request staged, status *Pending Director approval*, with audit hash — ✅

### E. Agent brain
- [x] **E1** System prompt rewritten around Q1–Q8 (Data → Analysis → Decision → Action), business language first; Q6 names the Monte Carlo — ✅
- [x] **E2** Remove V3 main-flow tools from the menu (backups kept) — ✅ (V3 code kept, off the menu)

### F. Quality & release
- [x] **F1** Unit tests: feed, conversions, gap, pricing, Monte Carlo (seeded), cards build, position, deadline rule, approver — ✅ 32/32 pass (12 V4 + 20 V3)
- [x] **F2** Local end-to-end run of Q1→Q6 — ✅ scripts/run_v4_local.py: 6/6 right tool + card, real Gemini + live data
- [x] **F3** Deploy to Gemini Enterprise — ✅ deployed 24 Sep 12:49 UTC (same engine 6842313636208181248)
- [ ] **F4** Live test, every question, twice — 🟡 extended flow (Q1–Q7 + GE) deployed 24 Sep 13:49 UTC; A2A endpoint: 3 runs, 0 errors, card on every Q1–Q7 (scripts/test_deployed_v4.py). 👤 Still to do: click through in the GE app UI
- [x] **F5** Demo script, crib sheet, README updated — ✅
- [ ] **F6** Commit + push — ⬜ **asks you first**

### Done already (safety)
- [x] V3 tagged `V3` for one-step rollback
- [x] Live-but-uncommitted V3 prompt tweaks saved as a patch

---

## 3. Out of scope (explicitly)
- GAIL segment revenue/profit table — no reliable source found; don't show until pulled from the FY26 results PDF
- JKM live price — licensed (Platts); India spot is estimated as TTF + $0.50 and labelled
- "Sell US cargo in Europe, backfill with Qatar" — invalid while Qatar is offline
- Multivariate OLS — explains, doesn't forecast
