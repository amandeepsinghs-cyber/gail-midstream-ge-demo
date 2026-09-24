# Engineering Build Guide — GAIL Pipeline Agent V3

## 1. Layout (V3-relevant files)
```
app/
├── agent.py                        # ADK agent, system instruction (4 beats), A2UI emit priority
├── scenario.py                     # Single source of truth: shortfall(), lng_decision(), forecast(), storyline()
├── contracts.py                    # Pydantic response schemas
├── analytics/
│   ├── sarimax_linepack.py         # Regression-with-SARIMA-errors engine (fit, run_scenarios, build_setpoint)
│   └── lng_landed_cost.py          # evaluate_options(): delivered $/MMBtu + arrival-vs-cover screen
├── integration/
│   ├── tools.py                    # ADK tools: audit, evaluate_lng_supply_options, run_sarimax_linepack_forecast, publish_decision_brief
│   ├── gcs_connector.py            # GCS-first loaders with local fixture fallback; report upload
│   └── agent_card.py               # A2A agent card / skills
├── render/
│   ├── a2ui_emit.py                # A2UI surfaces: spatial, LNG, SARIMAX, decision
│   └── forecast_vega.py            # Two-scenario forecast chart
└── synthesis/executive_report_compiler.py   # HTML briefing with "Decision on one page" box
fixtures/
├── generate_fixtures.py            # Physically consistent demo scenario
├── gail_hvj_scada_telemetry_72h.csv
├── customer_nominations_24h.json
└── lng_market_snapshot.json        # Illustrative prices
tests/                              # incl. test_storyline.py (cross-beat consistency)
```

## 2. Model design notes
- **SARIMAX:** line-pack `P_t` regressed on the **cumulative** net balance `cumsum(supply − demand)` with SARIMA errors. Using the raw net balance fails, because statsmodels' exog shifts the level, not the difference.
- **Fit quality on the fixtures:** β ≈ 0.109 (generator uses 0.125; sensor noise attenuates it), hold-out back-test (train 48h → predict 24h) error 0.33%, 95% band widens ±0.5 → ±2.2 kg/cm² over 24h. Fit is ~4s and cached per process.
- **Future exog:** `last_cum_imbalance + cumsum(future_net)`, computed for two scenarios: without action, and with a +4.0 MMSCMD swap.
- **LNG:** delivered cost = FOB/hub + freight + regas + margins. An option is screened out if arrival days exceed inventory cover.
- **Synthetic history:** flat day-ahead compressor schedule vs. diurnal demand → visible pack/draft cycle; AR(1) sensor noise (σ 0.25, φ 0.8) → realistic widening cone. Chart shows last 48h actuals + both scenario cones (80%/95%).

## 3. Data flow
The loaders read `gs://gail-midstream-ge-demo-datalake/raw/...` first. If a required column is missing (`net_balance_mmscmd`, `baseline_offtake_mmscmd`), they fall back to local `fixtures/`. After regenerating fixtures, re-upload them to `raw/scada/`, `raw/customer_nominations/` and `raw/lng_market/`.

## 4. A2UI
Only one card is emitted per turn. Priority order: decision → LNG → SARIMAX → spatial/other. Charts are Vega-Lite and validated with altair in the tests.

## 5. Verify & deploy
```bash
uv sync --extra dev
.venv/bin/python -m pytest -q
agents-cli deploy --project og-agentic-ecosystem
agents-cli deploy --status
```
**Live A2A smoke test:** POST JSON-RPC `message/send` to
`https://asia-south1-aiplatform.googleapis.com/reasoningEngines/v1/projects/349946979746/locations/asia-south1/reasoningEngines/6842313636208181248/api/a2a/app`
with each of the four prompts in [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

**IAM required on the agent SA:** `roles/serviceusage.serviceUsageConsumer`, plus `roles/storage.objectAdmin` on the data-lake bucket.
