# Presenter Crib Sheet: "One Morning at GAIL"
*One page. Print it or keep it on a second screen.*

---

## 1. Your opening frame (say this first)
> "You know this business far better than I do. I'll show you a **pattern** using a gas example: **any data → any model → any report → action**. Watch the pattern, not the gas."

## 2. GAIL's business in 5 lines
1. **GAIL moves gas.** It buys domestic gas and imported LNG (ships arrive at **Dahej**, Gujarat) and pushes it through **18,700 km** of pipelines.
2. **Customers:** fertilizer plants, city gas (CNG in autos, PNG in kitchens), power plants, industry.
3. **Every morning customers tell GAIL tomorrow's demand.** These are called **nominations**.
4. **The pipe is a buffer.** Gas stored in it under pressure is called **line-pack**, like water in an overhead tank. Take out more than comes in and pressure falls. Below **76** (the contract floor), GAIL can't deliver properly and pays penalties.
5. **To fill a gap, GAIL buys extra LNG:** an expensive last-minute ship (spot), a cheap ship that arrives too late, or a **swap** of cargo timing with Qatar.

## 3. The story in 3 sentences (memorise)
> "Customers want more gas tomorrow than we planned. Here's the cheapest way to get it that arrives in time. And here's proof the pipeline holds if we do it, and breaks tonight if we don't."

---

## 4. The four prompts (paste in order, same chat)

| # | Paste | Point at | Say (one line) | Swap for yours |
|---|---|---|---|---|
| 1 | Show me today's grid flows and tomorrow's customer nominations. | ⚠️ **4.0 MMSCMD shortfall** | "It joined three data sources and found a gap nobody asked about." | Finance: ledger + bank feed |
| 2 | What's the cheapest way to cover that shortfall? | Green bar, **₹70.3 Cr saved** | "Cheapest on paper arrives too late. It filtered that out, with fixed formulas, not guesswork." | Procurement: bids vs delivery dates |
| 3 | Can the grid carry it? Forecast Chhainsa for 24 hours. | Left: history. Right: **red breaks at 19:00**, green stays safe | "It learned the daily pattern, checked itself against yesterday (0.33% error), then showed tonight with and without action." | Any Excel forecast + "what if we act" |
| 4 | Brief management and raise the SAP order. | One-page decision + **report link** | "One page for the MD. SAP order staged for a human to approve." | Your MIS, board note, audit pack |

**Close:**
> "Four questions, one conversation. Nothing here was gas-specific except the data. **What's the 6 AM question on your desk?**"

---

## 5. Words you can skip
- **SARIMAX / β** → "a standard forecasting model, trained on 3 days, checked against yesterday."
- **Vijaipur +3.8% setpoint** → "and it tells the control room how much to turn up the compressor."
- **Henry Hub / JKM** → "one ship is cheaper but arrives too late."
- **Cones** → "the shaded area is its confidence; it widens because the future is uncertain."

## 6. Safe answers to likely questions

| If they ask… | Say |
|---|---|
| Is this real GAIL data? | "Illustrative data, real models. Plug in your data lake and the same flow runs live." |
| Does it connect to SCADA? | "It reads the historian and data lake, not the control system. That's deliberate, for security." |
| Will it act on its own? | "No. It stages the SAP order; a human approves." |
| How accurate is it? | "It predicted the last 24 hours with 0.33% error before forecasting the next 24." |
| Our problem is different | "That's the point. Swap in your data and your model; the pattern stays." |
| Something technical you don't know | "Great question for your engineers and ours. Let's take it offline." |

## 7. If something breaks
- Card doesn't show → type **"Show that as a chart."**
- It stalls → open a **new chat** and restart from prompt 1 (each step takes about 10s).
- The report link is slow → **"Summarise the decision in three bullets."**

**Before you go on:** warm up once in a separate chat 15 min before, confirm the GAIL logo shows, open the report link once, then start a fresh chat for the stage.
