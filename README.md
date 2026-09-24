# Decision Intelligence with Gemini Enterprise: "The Winter Call" (V4)

A Gemini Enterprise agent that helps GAIL's experts make one critical, high-value call by joining **GAIL's own data** with **the outside world**, then putting the action back into GAIL's systems:

> **GAIL data 🏢 + outside data 🌐 → risk-checked decision → approval + SAP (human approves)**

*"Bloomberg knows the market. SAP knows GAIL. Only Gemini Enterprise puts them in one decision."*

> [!IMPORTANT]
> **Market prices are LIVE** (Yahoo Finance: Henry Hub, TTF, Brent, USD/INR, EUR/USD and winter futures), and **news is live** (Google Search), so the numbers **change every day**.
> GAIL's contract book, winter supply plan, Dahej inventory, SAP open orders, budget ($22/MMBtu), risk limit (₹800 Cr), lead time (45 days) and delegation of authority are **SAMPLE data** in `gs://gail-midstream-ge-demo-datalake/raw/gail_internal/`. The recommendation depends on those sample policy numbers.
> Analyst forecasts (`fixtures/analyst_outlook.json`) are dated and sourced, but **a human should open each source before stage**.

---

## Explained simply

**The situation.** Qatar LNG is under force majeure in 2026. That outage is why TTF is near €74 and Brent above $100. GAIL's Qatar contract cargoes won't arrive this winter.

**The critical call.** Do we **lock in replacement cargoes now** at today's futures, or **wait** and hope prices fall?

**The thesis:** data first (GAIL's systems and the outside world), then **analysis**, then the **decision**, then **action**.

| # | Stage | Ask | Data joined | The "so what" (24 Sep rehearsal, live prices) |
|---|---|---|---|---|
| 1 | Data | **What is the impact of the Qatar force majeure on our winter gas supply?** | 🏢 contract book + supply plan · 🌐 news | 6 cargoes (19 TBtu) short Dec–Feb; ₹184 Cr per $1/MMBtu |
| 2 | Data | **Check our own position: inventory, customer commitments and what's already in SAP.** | 🏢 Dahej inventory, customers, SAP open orders and budget, lead time, delegation of authority | December cargoes must be contracted by **17 Oct (23 days)**; tanks can't absorb a missed month; no SAP order covers the gap |
| 3 | Data | **What is gas costing today, and what does that mean for our contracts and our budget?** | 🏢 contract formulas + SAP budget · 🌐 live prices + futures | US contract cargo ~$10.9 vs ~$24.9 spot; Qatar outage ≈ ₹2,060 Cr extra; lock-in ₹540 Cr over budget |
| 4 | Analysis | **How did we get here? Show me the last 5 years.** | 🌐 5-year weekly history | 2022 and 2026 spikes; TTF volatility ~90% a year |
| 5 | Analysis | **What do the experts expect?** | 🌐 analyst forecasts | 2027 consensus well below today, but a wide spread |
| 6 | Analysis → Decision | **Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?** | 🌐 futures, volatility, consensus × 🏢 everything above | 10,000 paths: waiting saves ~₹118 Cr on average but the worst case is +₹2,312 Cr, beyond the ₹800 Cr limit → **lock in all 6** |
| 7 | Action | **Prepare the approval and stage it in SAP.** | 🏢 SAP + delegation of authority | Approver picked by value; HTML memo in GCS; SAP purchase requisition **AWAITING APPROVAL** |
| 8 *(optional)* | — | Can the pipeline take the volumes? | 🏢 SCADA (illustrative) | V3 SARIMAX line-pack chart (illustrative +4.0 MMSCMD, not the winter gap) |

Ask **"Why do we need Gemini Enterprise for this?"** and the agent explains the value itself.

---

## Demo flow
The presenter crib sheet is in **[PRESENTER_CRIB_SHEET.md](PRESENTER_CRIB_SHEET.md)**, and the full stage script and talk-track are in [DEMO_SCRIPT.md](DEMO_SCRIPT.md). Feature status: [V4_FEATURE_CHECKLIST.md](V4_FEATURE_CHECKLIST.md).

If a card is missing, type `Show that as a chart.` If it gets stuck, open a new chat and start again at question 1.

The previous "One Morning at GAIL" (V3) flow is preserved at git tag `V3`.

### Rehearsal checklist
- [ ] New GE chat → **GAIL Gas Supply Decision Agent** (GAIL logo visible)
- [ ] Q1 shows the winter gap card with 🏢/🌐 source tags
- [ ] Q3 shows prices marked **Live** (not "last saved" or "bundled")
- [ ] Q2 shows the deadline chart, Dahej tanks, customers, SAP orders and budget
- [ ] Q3 shows live prices plus lock-in cost vs the SAP budget
- [ ] Q6 opens with the Monte Carlo method, then the fan chart and a recommendation checked against the risk limit and GAIL's position
- [ ] Q7 names the approver; memo link opens (signed in to the demo account); SAP shows AWAITING APPROVAL

Local rehearsal with real Gemini and live data: `.venv/bin/python scripts/run_v4_local.py`

---

## For engineers

### V4 tools (`app/integration/v4_tools.py`)

| Q | Tool | Model / logic |
|---|---|---|
| 1 | `assess_winter_supply_gap` | Contract book (Qatar FM) + winter plan → gap in cargoes/TBtu, ₹ per $1 |
| 3 | `get_live_gas_market` | Yahoo chart API; TTF €/MWh → $/MMBtu; contract landed cost vs spot replacement |
| 4 | `get_gas_price_history` | 5-year weekly closes; annualised volatility |
| 5 | `get_analyst_price_outlook` | Verified forecasts only; consensus = median of 2027 forecasts |
| 2 | `check_gail_position` | Dahej usable stock vs one month's gap; must-supply customers and compensation; SAP open POs and budget (`sap_open_position.json`); contracting deadline = delivery month − lead time; approver from the delegation of authority |
| 6 | `evaluate_winter_procurement` | 10,000-path TTF Monte Carlo (weekly, 52w, seed 42) centred on the consensus; LOCK_ALL / HEDGE_HALF / WAIT; **hard rule:** waiting is priced at each month's contracting deadline, and past-deadline months are forced to lock; cheapest expected cost within the P95 risk limit |
| 7 | `prepare_procurement_approval` | HTML memo (incl. "checked against GAIL's position") → GCS `curated/executive_reports/`; staged SAP purchase requisition routed to the approver by value |
| news | `market_news_agent` (AgentTool) | Google Search grounding |

Market data fallback: live Yahoo → last saved copy in GCS → bundled `fixtures/latest_snapshot.json`. Each card shows which was used. `GAIL_MARKET_OFFLINE=1` forces the bundled copy (used by the tests). Refresh the bundled copy with `python -m app.market.yahoo_feed`.

### V3 tools (still available)

| Step | Tool | Model / logic |
|---|---|---|
| See | `audit_grid_and_weather_risk` | Revised vs baseline nominations → shortfall |
| Analyse | `evaluate_lng_supply_options` | Delivered cost = FOB + freight + regas + margins; screen out options arriving after inventory cover |
| Prove | `run_sarimax_linepack_forecast` | SARIMAX(1,1,0)×(1,0,0)₂₄ on cumulative supply–demand balance; 48h→24h hold-out back-test; two exogenous scenarios; 80/95% intervals |
| Act | `publish_decision_brief` | HTML brief to GCS + staged SAP S/4HANA order |

- **Project:** `og-agentic-ecosystem` (asia-south1) · **Reasoning Engine:** `6842313636208181248`
- **Service account:** `gail-grid-agent@og-agentic-ecosystem.iam.gserviceaccount.com`
- **Data lake:** `gs://gail-midstream-ge-demo-datalake` (`raw/scada/`, `raw/customer_nominations/`, `raw/lng_market/`, `raw/gail_internal/`, `market/`, `curated/executive_reports/`)
- **GE app:** `oil-and-gas-agentic-transf_1788683272432`
- Design notes: [BUILD.md](BUILD.md)

```bash
uv sync --extra dev
.venv/bin/python -m pytest -q                            # 32 tests (20 V3 + 12 V4)
.venv/bin/python fixtures/generate_fixtures.py           # regenerate demo data (then re-upload to GCS raw/)
agents-cli deploy --project og-agentic-ecosystem         # ~6 min
```
